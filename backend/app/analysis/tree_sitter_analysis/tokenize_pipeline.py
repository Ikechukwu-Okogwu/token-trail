"""
End-to-end leaf-token fingerprint pipeline: pair → group → filter → dye coverage.

Returns dye ``similarity`` (merged token coverage) and kept ``groups``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    filter_groups,
    load_group_filter_config,
    load_type_mapping_csv,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_interpretation import (
    DyeResult,
    dye_tokens,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.grouping_fingerprint_pairs import (
    FingerprintPairGroup,
    grouping_fingerprint_pairs,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.json_kgram_strategy import (
    JsonLeafKgramStrategy,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import Token
from app.analysis.tree_sitter_analysis.template_exclusion import strip_template_classes


_TOKENIZE_WORKFLOW_DIR = Path(__file__).resolve().parent / "tokenize_workflow"
DEFAULT_TYPE_MAPPING_PATH = _TOKENIZE_WORKFLOW_DIR / "type_mapping.csv"
DEFAULT_GROUP_FILTER_CONFIG_PATH = _TOKENIZE_WORKFLOW_DIR / "group_filtering_config.json"


@dataclass(frozen=True)
class TokenizePipelineResult:
    """Output of :func:`run_tokenize_similarity_pipeline`."""

    similarity: float
    groups: tuple[FingerprintPairGroup, ...]
    dye: DyeResult
    tokens_a: tuple[Token, ...]
    tokens_b: tuple[Token, ...]
    strategy_k: int

    def matching_regions_as_dicts(self) -> list[dict[str, int]]:
        """
        One dict per kept group: inclusive 1-based line spans on each side.

        Keys match API / Mongo: ``leftStartLine``, ``leftEndLine``,
        ``rightStartLine``, ``rightEndLine``.
        """
        from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
            group_token_span_bounds,
        )

        tokens_a = self.tokens_a
        tokens_b = self.tokens_b
        k = self.strategy_k
        na, nb = len(tokens_a), len(tokens_b)
        regions: list[dict[str, int]] = []
        for g in self.groups:
            lo_a, hi_a = group_token_span_bounds(g, side="a", k=k, n_tokens=na)
            lo_b, hi_b = group_token_span_bounds(g, side="b", k=k, n_tokens=nb)
            if hi_a < lo_a or hi_b < lo_b:
                continue
            ls_a = min(tokens_a[i].start_line for i in range(lo_a, hi_a + 1))
            le_a = max(tokens_a[i].end_line for i in range(lo_a, hi_a + 1))
            ls_b = min(tokens_b[i].start_line for i in range(lo_b, hi_b + 1))
            le_b = max(tokens_b[i].end_line for i in range(lo_b, hi_b + 1))
            regions.append(
                {
                    "leftStartLine": ls_a,
                    "leftEndLine": le_a,
                    "rightStartLine": ls_b,
                    "rightEndLine": le_b,
                }
            )
        return regions


def _fingerprint_pairs_for_two_java_codes(
    code_a: str,
    code_b: str,
    *,
    strategy: JsonLeafKgramStrategy,
    winnow_window: int,
    max_pos_each: int,
):
    from app.analysis.tree_sitter_analysis.tokenize_workflow.fingerprint_pairing import (
        pairing_list_from_winnow_fingerprint_sequences,
        winnow_fingerprint_sequence,
    )

    tokens_a = strategy.tokens_for_kgram(code_a)
    tokens_b = strategy.tokens_for_kgram(code_b)
    raw_a = strategy.compute_kgram_fingerprints(tokens_a)
    raw_b = strategy.compute_kgram_fingerprints(tokens_b)
    win_a = winnow_fingerprint_sequence(raw_a, winnow_window)
    win_b = winnow_fingerprint_sequence(raw_b, winnow_window)
    return pairing_list_from_winnow_fingerprint_sequences(
        win_a,
        win_b,
        max_pos_each=max_pos_each,
    )


def run_tokenize_similarity_pipeline(
    code_a: str,
    code_b: str,
    *,
    template: str = "",
    strategy: JsonLeafKgramStrategy | None = None,
    type_mapping_path: str | Path | None = None,
    group_filter_config_path: str | Path | None = None,
    winnow_window: int = 4,
    max_pos_each: int = 100,
    min_group_size: int = 4,
    delta_tol: int = 5,
    max_gap: int = 120,
    default_categories: Sequence[str] = ("unmapped",),
) -> TokenizePipelineResult:
    """
    1. If ``template`` is non-blank, strip top-level template classes from both
       ``code_a`` and ``code_b`` via AST byte-span removal before tokenization.
    2. Tokenize both sides (strategy), Winnow k-grams, pair, group.
    3. Load type mapping + filter config; ``filter_groups`` on raw groups.
    4. ``dye_tokens`` on kept groups → coverage ``similarity`` = (marked_a + marked_b) / (n_a + n_b).

    Raises:
        ValueError: if either source is empty/whitespace-only (before or after template
            exclusion), or either side has no tokens after tokenization.
    """
    if not (code_a or "").strip() or not (code_b or "").strip():
        raise ValueError(
            "run_tokenize_similarity_pipeline: code_a and code_b must be non-empty "
            "(non-whitespace)"
        )

    if (template or "").strip():
        code_a = strip_template_classes(code_a, template)
        code_b = strip_template_classes(code_b, template)
        if not (code_a or "").strip() or not (code_b or "").strip():
            raise ValueError(
                "run_tokenize_similarity_pipeline: after template exclusion, both "
                "code_a and code_b must be non-empty (non-whitespace)"
            )

    strategy = strategy or JsonLeafKgramStrategy(k=5)
    map_path = Path(type_mapping_path or DEFAULT_TYPE_MAPPING_PATH)
    filt_path = Path(group_filter_config_path or DEFAULT_GROUP_FILTER_CONFIG_PATH)
    if not map_path.is_file():
        raise FileNotFoundError(f"type mapping not found: {map_path}")
    if not filt_path.is_file():
        raise FileNotFoundError(f"group filter config not found: {filt_path}")

    tokens_a = strategy.tokens_for_kgram(code_a)
    tokens_b = strategy.tokens_for_kgram(code_b)
    if not tokens_a or not tokens_b:
        raise ValueError(
            "run_tokenize_similarity_pipeline: both sides need at least one leaf token "
            f"(got len(tokens_a)={len(tokens_a)}, len(tokens_b)={len(tokens_b)})"
        )

    pairs = _fingerprint_pairs_for_two_java_codes(
        code_a,
        code_b,
        strategy=strategy,
        winnow_window=winnow_window,
        max_pos_each=max_pos_each,
    )
    raw_groups = grouping_fingerprint_pairs(
        pairs,
        min_group_size=min_group_size,
        delta_tol=delta_tol,
        max_gap=max_gap,
    )

    type_mapping = load_type_mapping_csv(map_path)
    filter_config = load_group_filter_config(filt_path)

    k = strategy.k
    kept = filter_groups(
        raw_groups,
        tokens_a=tokens_a,
        tokens_b=tokens_b,
        k=k,
        type_mapping=type_mapping,
        config=filter_config,
        default_categories=default_categories,
    )

    dye = dye_tokens(
        kept,
        n_tokens_a=len(tokens_a),
        n_tokens_b=len(tokens_b),
        k=k,
    )

    return TokenizePipelineResult(
        similarity=dye.similarity,
        groups=tuple(kept),
        dye=dye,
        tokens_a=tuple(tokens_a),
        tokens_b=tuple(tokens_b),
        strategy_k=k,
    )
