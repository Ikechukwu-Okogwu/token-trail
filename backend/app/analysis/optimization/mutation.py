"""
Random mutation of :class:`~app.analysis.config.TokenizePipelineConfig`.

Policy is driven by ``mutation_config.json`` (plain dict). Does not mutate
``type_mapping`` or ``strategy`` in this simple version.
"""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path

from app.analysis.config import TokenizePipelineConfig
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    GroupFilterConfig,
    GroupFilterFeature,
)

_PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_MUTATION_CONFIG_PATH = _PACKAGE_DIR / "mutation_config.json"


def load_mutation_config(path: str | Path | None = None) -> dict:
    """Load JSON object as ``dict`` (no schema class)."""
    p = Path(DEFAULT_MUTATION_CONFIG_PATH if path is None else path)
    return json.loads(p.read_text(encoding="utf-8"))


def _clamp_int(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, x))


def _clampf(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _pair_bounds(key: str, mc: dict) -> tuple[float | int, float | int]:
    pair = mc["bounds"][key]
    return pair[0], pair[1]


def _maybe_int(rng: random.Random, mc: dict, key: str, value: int) -> int:
    if rng.random() >= mc["prob_int_param"]:
        return value
    lo, hi = _pair_bounds(key, mc)
    lo_i, hi_i = int(lo), int(hi)
    delta = rng.randint(-mc["int_step_max"], mc["int_step_max"])
    return _clamp_int(value + delta, lo_i, hi_i)


def _maybe_float_global(rng: random.Random, mc: dict, key: str, value: float) -> float:
    if rng.random() >= mc["prob_float_global"]:
        return value
    lo, hi = _pair_bounds(key, mc)
    d = mc["float_delta"]
    return _clampf(value + rng.uniform(-d, d), float(lo), float(hi))


def _mutate_interval(
    rng: random.Random, lo: float, hi: float, jitter: float
) -> tuple[float, float]:
    lo2 = _clampf(lo + rng.uniform(-jitter, jitter), 0.0, 1.0)
    hi2 = _clampf(hi + rng.uniform(-jitter, jitter), 0.0, 1.0)
    if lo2 > hi2:
        m = (lo2 + hi2) / 2.0
        lo2, hi2 = m, m
    return lo2, hi2


def _mutate_feature(
    rng: random.Random, feat: GroupFilterFeature, mc: dict
) -> GroupFilterFeature:
    intervals = dict(feat.intervals)
    if rng.random() < mc["prob_feature_interval"]:
        intervals = {
            cat: _mutate_interval(rng, lo, hi, mc["interval_jitter"])
            for cat, (lo, hi) in intervals.items()
        }

    contrib = feat.contribution
    if rng.random() < mc["prob_feature_contribution"]:
        lo, hi = _pair_bounds("contribution", mc)
        contrib = _clampf(
            contrib + rng.uniform(-mc["float_delta"], mc["float_delta"]),
            float(lo),
            float(hi),
        )

    weight = feat.weight
    if rng.random() < mc["prob_feature_weight"]:
        lo, hi = _pair_bounds("weight", mc)
        weight = _clampf(
            weight + rng.uniform(-mc["float_delta"] * 3, mc["float_delta"] * 3),
            float(lo),
            float(hi),
        )
        if weight <= 0:
            weight = float(lo)

    return replace(
        feat,
        intervals=intervals,
        contribution=contrib,
        weight=weight,
    )


def _duplicate_feature(rng: random.Random, feats: tuple[GroupFilterFeature, ...]) -> GroupFilterFeature:
    src = feats[rng.randrange(len(feats))]
    tag = rng.randrange(1_000_000, 9_999_999)
    return replace(
        src,
        name=f"{src.name}_dup_{tag}",
        intervals={k: tuple(v) for k, v in src.intervals.items()},
    )


def mutate_pipeline_config(
    config: TokenizePipelineConfig,
    mutation_cfg: dict | None = None,
    *,
    rng: random.Random | None = None,
    config_path: str | Path | None = None,
) -> TokenizePipelineConfig:
    """
    Return a new config after in-place random edits (structure copied, not shared).

    ``mutation_cfg``: defaults to ``mutation_config.json`` next to this module.
    ``config_path``: optional path for :func:`load_mutation_config` override.
    ``rng``: optional; if ``None``, uses ``random_seed`` from JSON when set, else system RNG.
    """
    mc = mutation_cfg if mutation_cfg is not None else load_mutation_config(config_path)
    if rng is None:
        seed = mc.get("random_seed")
        rng = random.Random(seed if seed is not None else None)

    k = _maybe_int(rng, mc, "k", config.k)
    winnow_window = _maybe_int(rng, mc, "winnow_window", config.winnow_window)
    max_pos_each = _maybe_int(rng, mc, "max_pos_each", config.max_pos_each)
    min_group_size = _maybe_int(rng, mc, "min_group_size", config.min_group_size)
    min_group_size = max(2, min_group_size)
    delta_tol = _maybe_int(rng, mc, "delta_tol", config.delta_tol)
    max_gap = _maybe_int(rng, mc, "max_gap", config.max_gap)

    gfc = config.group_filter_config
    keep = _maybe_float_global(rng, mc, "keep_threshold", gfc.keep_threshold)
    default_sim = _maybe_float_global(
        rng, mc, "default_similarity_no_match", gfc.default_similarity_no_match
    )

    feats = tuple(_mutate_feature(rng, f, mc) for f in gfc.features)
    if (
        feats
        and rng.random() < mc["prob_duplicate_feature"]
        and len(feats) < 24
    ):
        feats = feats + (_duplicate_feature(rng, feats),)

    new_gfc = GroupFilterConfig(
        keep_threshold=keep,
        default_similarity_no_match=default_sim,
        features=feats,
    )

    return replace(
        config,
        k=k,
        winnow_window=winnow_window,
        max_pos_each=max_pos_each,
        min_group_size=min_group_size,
        delta_tol=delta_tol,
        max_gap=max_gap,
        group_filter_config=new_gfc,
    )
