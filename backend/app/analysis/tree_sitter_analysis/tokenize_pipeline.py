"""
End-to-end leaf-token fingerprint pipeline: pair → group → filter → dye coverage.

Returns dye ``similarity`` (merged token coverage) and kept ``groups``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.analysis.config.pipeline_config import (
    TokenizePipelineConfig,
    build_kgram_strategy,
    load_tokenize_pipeline_config_for_language,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import filter_groups
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_deduplicate import (
    dedupe_subsumed_groups,
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
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_preprocess import (
    leaf_tokens_and_truth_for_filter,
)


@dataclass(frozen=True)
class TokenizePipelineResult:
    """Output of :func:`run_tokenize_similarity_pipeline`."""

    similarity: float
    groups: tuple[FingerprintPairGroup, ...]
    dye: DyeResult
    tokens_a: tuple[Token, ...]
    tokens_b: tuple[Token, ...]
    strategy_k: int
    parse_quality_a: float = 1.0
    parse_quality_b: float = 1.0

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


def _fingerprint_pairs_from_tokens(
    tokens_a: Sequence[Token],
    tokens_b: Sequence[Token],
    *,
    strategy: JsonLeafKgramStrategy,
    winnow_window: int,
    max_pos_each: int,
):
    from app.analysis.tree_sitter_analysis.tokenize_workflow.fingerprint_pairing import (
        pairing_list_from_winnow_fingerprint_sequences,
        winnow_fingerprint_sequence,
    )

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
    config: TokenizePipelineConfig | None = None,
    language: str = "java",
    template: str = "",
) -> TokenizePipelineResult:
    """
    1. Resolve ``config``: if ``None``, load default bundle for ``language`` via
       :func:`app.analysis.config.pipeline_config.load_tokenize_pipeline_config_for_language`.
    2. Build per-side leaf tokens and truth tables using ``config.type_mapping`` and
       ``config.default_categories``. If ``template`` is non-blank, tokens on lines
       that exactly match a non-blank template line get ``to_drop`` (language-agnostic;
       see :mod:`template_exclusion`). Tokenizer follows ``language`` (``java`` / ``c`` / ``cpp``).
    3. Winnow k-grams, pair, group (parameters from ``config``).
    4. ``filter_groups`` with ``config.group_filter_config`` and pre-built truth tables.
    5. ``dedupe_subsumed_groups``, then ``dye_tokens`` → ``similarity``.

    Raises:
        ValueError: if either source is empty/whitespace-only, or if either side has
            no leaf tokens after ``to_drop`` (treated as unusable for this pipeline).
    """
    lang = (language or "").strip().lower()
    if config is None:
        config = load_tokenize_pipeline_config_for_language(lang)

    if not (code_a or "").strip() or not (code_b or "").strip():
        raise ValueError(
            "run_tokenize_similarity_pipeline: code_a and code_b must be non-empty "
            "(non-whitespace)"
        )

    strategy = build_kgram_strategy(config)
    type_mapping = config.type_mapping
    filter_cfg = config.group_filter_config
    default_categories = config.default_categories

    tokens_a, truth_a, pqs_a = leaf_tokens_and_truth_for_filter(
        code_a,
        type_mapping,
        default_categories=default_categories,
        language=lang,
        template=template,
    )
    tokens_b, truth_b, pqs_b = leaf_tokens_and_truth_for_filter(
        code_b,
        type_mapping,
        default_categories=default_categories,
        language=lang,
        template=template,
    )
    if not tokens_a or not tokens_b:
        raise ValueError(
            "run_tokenize_similarity_pipeline: both sides need at least one leaf token "
            f"(after to_drop filter: len(tokens_a)={len(tokens_a)}, "
            f"len(tokens_b)={len(tokens_b)})"
        )

    pairs = _fingerprint_pairs_from_tokens(
        tokens_a,
        tokens_b,
        strategy=strategy,
        winnow_window=config.winnow_window,
        max_pos_each=config.max_pos_each,
    )
    raw_groups = grouping_fingerprint_pairs(
        pairs,
        min_group_size=config.min_group_size,
        delta_tol=config.delta_tol,
        max_gap=config.max_gap,
    )

    k = strategy.k
    kept = filter_groups(
        raw_groups,
        tokens_a=tokens_a,
        tokens_b=tokens_b,
        k=k,
        type_mapping=type_mapping,
        config=filter_cfg,
        default_categories=default_categories,
        truth_a=truth_a,
        truth_b=truth_b,
    )

    kept = dedupe_subsumed_groups(
        kept,
        k=k,
        n_tokens_a=len(tokens_a),
        n_tokens_b=len(tokens_b),
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
        parse_quality_a=pqs_a,
        parse_quality_b=pqs_b,
    )
