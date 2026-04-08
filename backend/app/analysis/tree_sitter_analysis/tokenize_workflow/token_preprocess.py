"""
Leaf token build for the tokenize pipeline: parse → full truth table → ``to_drop`` row filter.

Preserves row index alignment between the kept ``Token`` list and the truth
``DataFrame`` passed to ``filter_groups`` (without a ``to_drop`` column).
"""

from __future__ import annotations

import warnings
from collections.abc import Collection, Mapping, Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

from app.analysis.tree_sitter_analysis.template_exclusion import (
    submission_lines_matching_template,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.c_leaf_tokenize import (
    tokenize_c,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.cpp_leaf_tokenize import (
    tokenize_cpp,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.java_leaf_tokenize import (
    tokenize_java,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.java_pqs_veto import (
    lowercase_type_identifier_veto,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
    Token,
    mapped_category_columns,
    mapped_type_truth_table,
)

# Mapped category label: any token row with ``True`` here is removed from the stream.
TO_DROP_MAPPED_LABEL = "to_drop"

# Per-language *leaf* token types (keywords, type tokens) that reliably appear in
# valid code of that language. Used by ``compute_parse_quality_score`` to detect
# wrong-language content that tree-sitter silently misparses.
# These are leaf-level types from tree-sitter grammars — NOT internal/parent node types.
_EXPECTED_LEAF_TYPES: dict[str, frozenset[str]] = {
    "java": frozenset({
        # Keywords that tree-sitter emits as named leaf tokens
        "public", "private", "protected", "static", "final", "class", "interface",
        "extends", "implements", "new", "return", "void_type", "this", "super",
        "import", "package", "throws", "throw", "try", "catch", "finally",
        "if", "else", "for", "while", "do", "switch", "case", "break", "continue",
        "boolean_type", "integral_type", "floating_point_type",
        # Types
        "null_literal", "true", "false",
    }),
    "c": frozenset({
        "return", "if", "else", "for", "while", "do", "switch", "case", "break",
        "continue", "struct", "typedef", "enum", "union", "sizeof",
        "void", "auto", "extern", "static", "register", "const", "volatile",
        "signed", "unsigned",
        "primitive_type",
        # NOTE: type_identifier deliberately excluded — it matches any identifier
        # tree-sitter interprets as a type name, including Python keywords (def,
        # import, etc.) when Python code is parsed as C, inflating PQS.
        "null", "true", "false",
    }),
    "cpp": frozenset({
        "return", "if", "else", "for", "while", "do", "switch", "case", "break",
        "continue", "class", "struct", "typedef", "enum", "union", "sizeof",
        "void", "auto", "extern", "static", "register", "const", "volatile",
        "namespace", "using", "public", "private", "protected", "virtual",
        "template", "typename", "new", "delete", "throw", "try", "catch",
        "primitive_type",
        # NOTE: type_identifier excluded — see C set comment above.
        "null", "nullptr", "true", "false",
    }),
}

# PQS below this threshold triggers a low-parse-quality warning.
PARSE_QUALITY_THRESHOLD = 0.002


def compute_parse_quality_score(
    tokens: Sequence[Token], *, language: str
) -> float:
    """Fraction of leaf tokens whose type is in the expected leaf-type set.

    For language-mismatch detection, the key insight is that wrong-language
    code parsed by tree-sitter produces a very different leaf token type
    distribution.  For example, valid Java code always has keywords like
    ``public``, ``class``, ``static``, ``void_type``, ``integral_type`` as
    leaf tokens.  Python code parsed as Java has none of these — only
    ``identifier``, ``type_identifier``, and punctuation.

    For Java only, if :func:`lowercase_type_identifier_veto`
    triggers, returns ``0.0`` regardless of the keyword hit rate (wrong-language
    heuristic consolidated here so all callers share one path).

    Returns 0.0 if there are no tokens.
    """
    if not tokens:
        return 0.0
    lang = (language or "").strip().lower()
    expected = _EXPECTED_LEAF_TYPES.get(lang, frozenset())
    if not expected:
        return 1.0  # no expectation → assume fine
    hits = sum(1 for t in tokens if t.type in expected)
    pqs = hits / len(tokens)
    if lang == "java" and lowercase_type_identifier_veto(tokens):
        return 0.0
    return pqs


# Hard rejection threshold for upload-time validation.
# Below this, the merged source is almost certainly not the expected language.
# Calibrated against: Python-in-Java=0.045, JS-in-Java=0.024, valid-Java-min=0.133,
# Python-in-C=0.022–0.037 (class/import-heavy), valid-C-min=0.101.
# Gap: worst-valid (0.101 C) vs threshold (0.05) = 2.0x safety margin.
UPLOAD_REJECT_PQS_THRESHOLD = 0.05

# Minimum token count for PQS to be meaningful.  Very short files
# (e.g. a single comment line) have unreliable PQS — skip the check.
UPLOAD_MIN_TOKENS_FOR_PQS = 8


def quick_parse_quality(code: str, *, language: str) -> tuple[float, int]:
    """Tokenize *code* and return ``(pqs, token_count)`` without truth tables.

    This is a lightweight entry point for upload-time validation: it only
    needs the tokenizer and PQS logic, not pandas or the full pipeline.

    Returns ``(0.0, 0)`` for unsupported languages or empty code.
    """
    lang = (language or "").strip().lower()
    if not code.strip() or lang not in ("java", "c", "cpp"):
        return 0.0, 0
    if lang == "java":
        tokens = tokenize_java(code)
    elif lang == "c":
        tokens = tokenize_c(code)
    else:
        tokens = tokenize_cpp(code)
    pqs = compute_parse_quality_score(tokens, language=lang)
    return pqs, len(tokens)


def warn_error_leaves(tokens: Sequence[Token], *, language: str = "java") -> None:
    if any(t.type == "ERROR" for t in tokens):
        n_err = sum(1 for t in tokens if t.type == "ERROR")
        warnings.warn(
            f"{language} parse produced {n_err} ERROR leaf token(s); "
            "k-gram fingerprint may be unreliable until handled.",
            UserWarning,
            stacklevel=2,
        )


def _require_to_drop_column(
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str],
) -> None:
    cols = mapped_category_columns(type_mapping, default_categories=default_categories)
    if TO_DROP_MAPPED_LABEL not in cols:
        raise ValueError(
            "type_mapping must map at least one raw_type to "
            f"{TO_DROP_MAPPED_LABEL!r} (e.g. line_comment, block_comment in CSV). "
            f"Current mapped labels: {cols!r}"
        )


def leaf_tokens_and_truth_for_filter(
    code: str,
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str] = ("unmapped",),
    language: str = "java",
    template: str = "",
) -> tuple[list[Token], "pd.DataFrame", float]:
    """
    1. Leaf-tokenize source (``tokenize_java`` / ``tokenize_c`` / ``tokenize_cpp`` per ``language``).
    2. Possibly warn on ERROR leaves.
    3. Compute parse quality score (PQS) — fraction of tokens matching expected
       structural types for the language. Low PQS signals likely language mismatch.
    4. Full ``mapped_type_truth_table`` (includes ``to_drop`` when configured in CSV).
    5. If ``template`` is non-blank: lines in ``code`` that exactly match some
       non-blank template line (see :mod:`template_exclusion`) OR extra ``to_drop``
       for tokens whose ``start_line`` and ``end_line`` both lie on such lines
       (simplified rule; see project todo).
    6. Drop every token whose ``to_drop`` column is ``True``; drop the same rows from
       the frame, remove the ``to_drop`` column, ``reset_index(drop=True)``.

    Returns:
        (kept_tokens, truth_dataframe, parse_quality_score)

    Raises:
        ValueError: if ``to_drop`` is not among mapped category columns, or ``language``
            tokenize language is unsupported.
    """
    import pandas as pd

    if not code.strip():
        return [], pd.DataFrame(dtype=bool), 0.0

    _require_to_drop_column(type_mapping, default_categories=default_categories)

    lang = (language or "").strip().lower()
    if lang == "java":
        tokens = tokenize_java(code)
    elif lang == "c":
        tokens = tokenize_c(code)
    elif lang == "cpp":
        tokens = tokenize_cpp(code)
    else:
        raise ValueError(
            f"leaf_tokens_and_truth_for_filter: unsupported language {language!r} "
            "(expected 'java', 'c', or 'cpp')"
        )
    warn_error_leaves(tokens, language=lang)
    pqs = compute_parse_quality_score(tokens, language=lang)

    if pqs < PARSE_QUALITY_THRESHOLD:
        warnings.warn(
            f"{lang} parse quality score is very low ({pqs:.3f}); "
            "the source code may not be valid for this language "
            "(e.g. wrong language in file). "
            "Similarity results may be unreliable.",
            UserWarning,
            stacklevel=2,
        )

    truth_full = mapped_type_truth_table(
        tokens,
        type_mapping,
        default_categories=default_categories,
    )

    if (template or "").strip():
        match_lines = submission_lines_matching_template(code, template)
        if match_lines:
            col = truth_full[TO_DROP_MAPPED_LABEL].to_numpy(dtype=bool, copy=True)
            for i, tok in enumerate(tokens):
                if tok.start_line in match_lines and tok.end_line in match_lines:
                    col[i] = True
            truth_full[TO_DROP_MAPPED_LABEL] = col

    drop_col = truth_full[TO_DROP_MAPPED_LABEL]
    keep = ~drop_col.to_numpy(dtype=bool)
    if len(keep) != len(tokens):
        raise RuntimeError("truth table row count must match token count")

    tokens_kept = [tokens[i] for i in range(len(tokens)) if keep[i]]
    df_kept = (
        truth_full.loc[keep]
        .drop(columns=[TO_DROP_MAPPED_LABEL])
        .reset_index(drop=True)
    )

    return tokens_kept, df_kept, pqs
