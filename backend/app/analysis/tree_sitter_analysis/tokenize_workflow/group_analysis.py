"""
Group-level token-type statistics and optional filtering using a CSV type mapping.

One raw Tree-sitter leaf type may map to several ``mapped_type`` rows; each token
then contributes +1 to every mapped category it participates in, and category
proportions use total mass = sum of those contributions (proportions sum to 1).
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from app.analysis.tree_sitter_analysis.tokenize_workflow.grouping_fingerprint_pairs import (
    FingerprintPairGroup,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.token_fingerprint import (
    Token,
    _categories_for_raw_type,
    align_mapped_type_truth_tables,
    mapped_type_truth_table,
)


@dataclass(frozen=True)
class GroupTokenTypeStats:
    """Share of each mapped category (mass-normalized) for A/B spans of one group."""

    side_a: dict[str, float]
    side_b: dict[str, float]
    token_count_a: int
    token_count_b: int
    mass_a: int
    mass_b: int


@dataclass(frozen=True)
class GroupFilterFeature:
    """
    Conjunction over interval constraints: all ``mapped_type`` shares on **both**
    sides A and B must fall in ``[lo, hi]`` (inclusive).
    """

    name: str
    intervals: dict[str, tuple[float, float]]
    contribution: float
    weight: float
    role: str = "unspecified"


@dataclass(frozen=True)
class GroupFilterConfig:
    keep_threshold: float
    default_similarity_no_match: float
    features: tuple[GroupFilterFeature, ...]


@dataclass(frozen=True)
class GroupFilterEval:
    """Per-group filtering result."""

    matched_feature_names: tuple[str, ...]
    similarity: float
    keep: bool


def load_group_filter_config(path: str | Path) -> GroupFilterConfig:
    """Load ``group_filtering_config.json``."""
    path = Path(path)
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    thr = float(data["keep_threshold"])
    default_sim = float(data["default_similarity_no_match"])
    raw_feats: list[dict[str, Any]] = list(data.get("features") or [])
    features: list[GroupFilterFeature] = []
    for item in raw_feats:
        name = str(item["name"])
        role = str(item.get("role") or "unspecified")
        contribution = float(item["contribution"])
        weight = float(item["weight"])
        if weight <= 0:
            raise ValueError(f"feature {name!r}: weight must be > 0")
        intervals_raw: dict[str, Any] = dict(item["intervals"])
        intervals: dict[str, tuple[float, float]] = {}
        for k, pair in intervals_raw.items():
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError(f"feature {name!r}: interval for {k!r} must be [lo, hi]")
            lo, hi = float(pair[0]), float(pair[1])
            if lo > hi:
                raise ValueError(f"feature {name!r}: {k!r} has lo > hi")
            intervals[str(k)] = (lo, hi)
        features.append(
            GroupFilterFeature(
                name=name,
                intervals=intervals,
                contribution=contribution,
                weight=weight,
                role=role,
            )
        )
    return GroupFilterConfig(
        keep_threshold=thr,
        default_similarity_no_match=default_sim,
        features=tuple(features),
    )


def _ratio_in_interval(ratio: float, lo: float, hi: float) -> bool:
    return lo <= ratio <= hi


def feature_intervals_match(
    shares_a: Mapping[str, float],
    shares_b: Mapping[str, float],
    intervals: Mapping[str, tuple[float, float]],
) -> bool:
    """
    **Conjunction**: every mapped category in ``intervals`` must satisfy the interval
    on **both** sides. Missing category share treated as ``0.0``.
    """
    for cat, (lo, hi) in intervals.items():
        ra = float(shares_a.get(cat, 0.0))
        rb = float(shares_b.get(cat, 0.0))
        if not (_ratio_in_interval(ra, lo, hi) and _ratio_in_interval(rb, lo, hi)):
            return False
    return True


def evaluate_group_filter(
    group: FingerprintPairGroup,
    tokens_a: Sequence[Token],
    tokens_b: Sequence[Token],
    k: int,
    type_mapping: Mapping[str, Collection[str]],
    config: GroupFilterConfig,
    *,
    default_categories: Collection[str] = ("unmapped",),
    truth_a: pd.DataFrame | None = None,
    truth_b: pd.DataFrame | None = None,
) -> GroupFilterEval:
    """
    For each configured feature, if all interval constraints hold on **both** sides,
    include its ``(weight, contribution)`` in a **weighted mean**. If none match,
    ``similarity`` is ``config.default_similarity_no_match``.

    ``keep`` is True iff ``similarity >= config.keep_threshold``.
    """
    stats = group_tokentype_analysis(
        group,
        tokens_a,
        tokens_b,
        k,
        type_mapping,
        default_categories=default_categories,
        truth_a=truth_a,
        truth_b=truth_b,
    )
    matched: list[GroupFilterFeature] = []
    for feat in config.features:
        if feature_intervals_match(stats.side_a, stats.side_b, feat.intervals):
            matched.append(feat)

    if not matched:
        sim = config.default_similarity_no_match
    else:
        num = sum(f.weight * f.contribution for f in matched)
        den = sum(f.weight for f in matched)
        sim = num / den if den > 0 else config.default_similarity_no_match

    keep = sim >= config.keep_threshold
    return GroupFilterEval(
        matched_feature_names=tuple(f.name for f in matched),
        similarity=sim,
        keep=keep,
    )


def load_type_mapping_csv(
    path: str | Path,
) -> dict[str, frozenset[str]]:
    """
    Load ``raw_type,mapped_type`` rows; merge multiple ``mapped_type`` per ``raw_type``.

    Lines starting with ``#`` and empty lines are ignored.
    """
    path = Path(path)
    merged: dict[str, set[str]] = defaultdict(set)
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return {}
        for row in reader:
            raw = (row.get("raw_type") or "").strip()
            dst = (row.get("mapped_type") or "").strip()
            if not raw or not dst or raw.startswith("#"):
                continue
            merged[raw].add(dst)
    return {k: frozenset(v) for k, v in merged.items()}


def group_token_span_bounds(
    group: FingerprintPairGroup,
    *,
    side: Literal["a", "b"],
    k: int,
    n_tokens: int,
) -> tuple[int, int]:
    """
    Inclusive token index bounds covering all k-grams in ``group`` on one side.

    Uses ``pos_*_start`` / ``pos_*_end`` as k-gram **start** indices; last covered
    token index is ``pos_end + k - 1`` (clamped).
    """
    if n_tokens <= 0 or k < 1:
        return (0, -1)
    if side == "a":
        pos_lo, pos_hi = group.pos_a_start, group.pos_a_end
    else:
        pos_lo, pos_hi = group.pos_b_start, group.pos_b_end
    last = n_tokens - 1
    lo = max(0, min(pos_lo, last))
    hi = min(max(pos_hi + k - 1, lo), last)
    return lo, hi


def _categories_for_token(
    token: Token,
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str],
) -> frozenset[str]:
    return _categories_for_raw_type(
        token.type, type_mapping, default_categories=default_categories
    )


def _mass_counts_for_span(
    tokens: Sequence[Token],
    lo: int,
    hi: int,
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str],
) -> tuple[dict[str, int], int, int]:
    """Returns (category_count, total_mass, token_span_len). Empty span -> empty dict, 0, 0."""
    if hi < lo or lo < 0 or not tokens:
        return {}, 0, 0
    counts: dict[str, int] = defaultdict(int)
    total_mass = 0
    n = 0
    for i in range(lo, hi + 1):
        if i >= len(tokens):
            break
        n += 1
        for c in _categories_for_token(tokens[i], type_mapping, default_categories=default_categories):
            counts[c] += 1
            total_mass += 1
    return dict(counts), total_mass, n


def _mass_counts_from_truth_df(
    df: pd.DataFrame,
    lo: int,
    hi: int,
) -> tuple[dict[str, int], int, int]:
    """Slice ``df`` by token row index; mass = sum of booleans in the slice."""
    if hi < lo:
        return {}, 0, 0
    nrows = len(df)
    if nrows == 0 or lo >= nrows:
        return {}, 0, 0
    hi_c = min(hi, nrows - 1)
    if hi_c < lo:
        return {}, 0, 0
    sl = df.iloc[lo : hi_c + 1]
    token_count = len(sl)
    if sl.shape[1] == 0:
        return {}, 0, token_count
    sums = sl.sum(axis=0)
    total_mass = int(sums.sum())
    counts = {str(c): int(sums[c]) for c in sl.columns if int(sums[c]) > 0}
    return counts, total_mass, token_count


def _shares_from_counts(counts: Mapping[str, int], total_mass: int) -> dict[str, float]:
    if total_mass <= 0:
        return {}
    return {c: counts[c] / total_mass for c in counts}


def group_tokentype_analysis(
    group: FingerprintPairGroup,
    tokens_a: Sequence[Token],
    tokens_b: Sequence[Token],
    k: int,
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str] = ("unmapped",),
    truth_a: pd.DataFrame | None = None,
    truth_b: pd.DataFrame | None = None,
) -> GroupTokenTypeStats:
    """
    Mapped-category mass shares within the group's covered token span on each side.

    When ``truth_a`` and ``truth_b`` are provided (from ``mapped_type_truth_table``),
    slice those frames by the same span bounds instead of iterating tokens.
    """
    if (truth_a is None) ^ (truth_b is None):
        raise ValueError("truth_a and truth_b must both be set or both be None")

    na, nb = len(tokens_a), len(tokens_b)
    lo_a, hi_a = group_token_span_bounds(group, side="a", k=k, n_tokens=na)
    lo_b, hi_b = group_token_span_bounds(group, side="b", k=k, n_tokens=nb)

    if truth_a is not None:
        ca, ma, ta = _mass_counts_from_truth_df(truth_a, lo_a, hi_a)
        cb, mb, tb = _mass_counts_from_truth_df(truth_b, lo_b, hi_b)
    else:
        ca, ma, ta = _mass_counts_for_span(
            tokens_a, lo_a, hi_a, type_mapping, default_categories=default_categories
        )
        cb, mb, tb = _mass_counts_for_span(
            tokens_b, lo_b, hi_b, type_mapping, default_categories=default_categories
        )

    return GroupTokenTypeStats(
        side_a=_shares_from_counts(ca, ma),
        side_b=_shares_from_counts(cb, mb),
        token_count_a=ta,
        token_count_b=tb,
        mass_a=ma,
        mass_b=mb,
    )


def filter_groups(
    groups: Sequence[FingerprintPairGroup],
    *,
    tokens_a: Sequence[Token],
    tokens_b: Sequence[Token],
    k: int,
    type_mapping: Mapping[str, Collection[str]],
    config: GroupFilterConfig,
    default_categories: Collection[str] = ("unmapped",),
    truth_a: pd.DataFrame | None = None,
    truth_b: pd.DataFrame | None = None,
) -> list[FingerprintPairGroup]:
    """
    Keep groups whose type-share profile matches ``config`` (see ``evaluate_group_filter``).

    Builds aligned truth tables once unless ``truth_a`` / ``truth_b`` are passed in.
    """
    if truth_a is None and truth_b is None:
        truth_a = mapped_type_truth_table(
            tokens_a, type_mapping, default_categories=default_categories
        )
        truth_b = mapped_type_truth_table(
            tokens_b, type_mapping, default_categories=default_categories
        )
    elif truth_a is None or truth_b is None:
        raise ValueError("truth_a and truth_b must both be set or both be None")
    truth_a, truth_b = align_mapped_type_truth_tables(truth_a, truth_b)

    kept: list[FingerprintPairGroup] = []
    for g in groups:
        ev = evaluate_group_filter(
            g,
            tokens_a,
            tokens_b,
            k,
            type_mapping,
            config,
            default_categories=default_categories,
            truth_a=truth_a,
            truth_b=truth_b,
        )
        if ev.keep:
            kept.append(g)
    return kept
