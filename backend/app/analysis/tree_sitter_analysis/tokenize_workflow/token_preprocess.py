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
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
    Token,
    mapped_category_columns,
    mapped_type_truth_table,
)

# Mapped category label: any token row with ``True`` here is removed from the stream.
TO_DROP_MAPPED_LABEL = "to_drop"


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
) -> tuple[list[Token], pd.DataFrame]:
    """
    1. Leaf-tokenize source (``tokenize_java`` / ``tokenize_c`` / ``tokenize_cpp`` per ``language``).
    2. Possibly warn on ERROR leaves.
    3. Full ``mapped_type_truth_table`` (includes ``to_drop`` when configured in CSV).
    4. If ``template`` is non-blank: lines in ``code`` that exactly match some
       non-blank template line (see :mod:`template_exclusion`) OR extra ``to_drop``
       for tokens whose ``start_line`` and ``end_line`` both lie on such lines
       (simplified rule; see project todo).
    5. Drop every token whose ``to_drop`` column is ``True``; drop the same rows from
       the frame, remove the ``to_drop`` column, ``reset_index(drop=True)``.

    Raises:
        ValueError: if ``to_drop`` is not among mapped category columns, or ``language``
            tokenize language is unsupported.
    """
    import pandas as pd

    if not code.strip():
        return [], pd.DataFrame(dtype=bool)

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

    return tokens_kept, df_kept
