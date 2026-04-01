"""
Crossover for ``GroupFilterConfig`` / ``TokenizePipelineConfig``.

Pairing: each feature on the **anchor** side matches **at most one** feature on the
**donor** side (greedy by overlap size, then Jaccard on interval keys). Only pairs
with ``|keys_a & keys_b| >= min_overlap_keys`` are allowed; optional same-``role``
filter.

For a matched pair: for each key in ``keys_a | keys_b``, interval comes from the
parent that owns the key; for keys in the **intersection**, uniformly pick one
parent per key. ``contribution`` / ``weight`` / ``name`` are blended from both;
``weight`` is clamped to be > 0.
"""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path
from typing import Any

from app.analysis.config import TokenizePipelineConfig
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    GroupFilterConfig,
    GroupFilterFeature,
)

_OPT_ROOT = Path(__file__).resolve().parent
DEFAULT_CROSSOVER_CONFIG_PATH = _OPT_ROOT / "crossover_config.json"


def load_crossover_config(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(DEFAULT_CROSSOVER_CONFIG_PATH if path is None else path)
    return json.loads(p.read_text(encoding="utf-8"))


def _feature_keys(f: GroupFilterFeature) -> frozenset[str]:
    return frozenset(f.intervals.keys())


def _pair_score(
    fa: GroupFilterFeature,
    fb: GroupFilterFeature,
    *,
    require_same_role: bool,
    min_overlap: int,
) -> tuple[int, float] | None:
    if require_same_role and fa.role != fb.role:
        return None
    ka, kb = _feature_keys(fa), _feature_keys(fb)
    inter = ka & kb
    if len(inter) < min_overlap:
        return None
    union = ka | kb
    jacc = len(inter) / len(union) if union else 0.0
    return (len(inter), jacc)


def _greedy_pairs(
    anchors: list[GroupFilterFeature],
    donors: list[GroupFilterFeature],
    rng: random.Random,
    xcfg: dict[str, Any],
) -> list[tuple[GroupFilterFeature, GroupFilterFeature | None]]:
    require_same_role = bool(xcfg.get("require_same_role_for_pairing", True))
    min_overlap = int(xcfg.get("min_overlap_keys", 1))
    idx_order = list(range(len(anchors)))
    rng.shuffle(idx_order)
    unused_donor: set[int] = set(range(len(donors)))
    out: list[tuple[GroupFilterFeature, GroupFilterFeature | None]] = [
        (anchors[i], None) for i in range(len(anchors))
    ]
    for i in idx_order:
        fa = anchors[i]
        best_j: int | None = None
        best_score: tuple[int, float] = (-1, -1.0)
        for j in unused_donor:
            sc = _pair_score(fa, donors[j], require_same_role=require_same_role, min_overlap=min_overlap)
            if sc is not None and sc > best_score:
                best_score = sc
                best_j = j
        if best_j is not None:
            out[i] = (fa, donors[best_j])
            unused_donor.remove(best_j)
    return out


def _cross_matched(
    fa: GroupFilterFeature,
    fb: GroupFilterFeature,
    rng: random.Random,
) -> GroupFilterFeature:
    ka, kb = _feature_keys(fa), _feature_keys(fb)
    inter = ka & kb
    union = ka | kb
    new_iv: dict[str, tuple[float, float]] = {}
    for k in sorted(union):
        if k in inter:
            src = fa if rng.random() < 0.5 else fb
            lo, hi = src.intervals[k]
            new_iv[k] = (float(lo), float(hi))
        elif k in ka:
            lo, hi = fa.intervals[k]
            new_iv[k] = (float(lo), float(hi))
        else:
            lo, hi = fb.intervals[k]
            new_iv[k] = (float(lo), float(hi))
    name = f"{fa.name}_x_{fb.name}"
    if len(name) > 120:
        name = name[:117] + "..."
    contrib = fa.contribution if rng.random() < 0.5 else fb.contribution
    weight = fa.weight if rng.random() < 0.5 else fb.weight
    if weight <= 0:
        weight = max(fa.weight, fb.weight, 1e-6)
    role = fa.role
    return GroupFilterFeature(
        name=name,
        intervals=new_iv,
        contribution=contrib,
        weight=weight,
        role=role,
    )


def crossover_group_filter_config(
    parent_a: GroupFilterConfig,
    parent_b: GroupFilterConfig,
    rng: random.Random,
    xcfg: dict[str, Any] | None = None,
) -> GroupFilterConfig:
    """
    Anchor = ``parent_a`` features (each paired at most once with ``parent_b``).
    Unmatched anchors: keep with ``prob_keep_unmatched_feature``.
    Donors never paired: same probabilistic keep (symmetric spill).
    """
    mc = xcfg if xcfg is not None else load_crossover_config()
    p_keep = float(mc.get("prob_keep_unmatched_feature", 0.5))

    lista = list(parent_a.features)
    listb = list(parent_b.features)
    pairs = _greedy_pairs(lista, listb, rng, mc)
    used_donor_idx = {
        j
        for j in range(len(listb))
        if any(pairs[i][1] is listb[j] for i in range(len(lista)))
    }

    child_features: list[GroupFilterFeature] = []
    for i, (fa, fb) in enumerate(pairs):
        if fb is not None:
            child_features.append(_cross_matched(fa, fb, rng))
        else:
            if rng.random() < p_keep:
                child_features.append(fa)

    for j, fb in enumerate(listb):
        if j not in used_donor_idx:
            if rng.random() < p_keep:
                child_features.append(fb)

    keep_thr = (
        parent_a.keep_threshold if rng.random() < 0.5 else parent_b.keep_threshold
    )
    def_sim = (
        parent_a.default_similarity_no_match
        if rng.random() < 0.5
        else parent_b.default_similarity_no_match
    )

    return GroupFilterConfig(
        keep_threshold=keep_thr,
        default_similarity_no_match=def_sim,
        features=tuple(child_features),
    )


def crossover_pipeline_config(
    parent_a: TokenizePipelineConfig,
    parent_b: TokenizePipelineConfig,
    rng: random.Random | None = None,
    xcfg: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> TokenizePipelineConfig:
    """Uniform crossover on scalars; ``type_mapping`` / ``strategy`` / ``default_categories`` from one parent."""
    if rng is None:
        rng = random.Random()
    mc = xcfg if xcfg is not None else load_crossover_config(config_path)
    gfc = crossover_group_filter_config(
        parent_a.group_filter_config, parent_b.group_filter_config, rng, mc
    )

    def pick_bool() -> bool:
        return rng.random() < 0.5

    tm = parent_a.type_mapping if pick_bool() else parent_b.type_mapping
    strategy = parent_a.strategy if pick_bool() else parent_b.strategy
    dc = parent_a.default_categories if pick_bool() else parent_b.default_categories

    return replace(
        parent_a,
        type_mapping=tm,
        group_filter_config=gfc,
        strategy=strategy,
        k=parent_a.k if pick_bool() else parent_b.k,
        winnow_window=parent_a.winnow_window if pick_bool() else parent_b.winnow_window,
        max_pos_each=parent_a.max_pos_each if pick_bool() else parent_b.max_pos_each,
        min_group_size=parent_a.min_group_size if pick_bool() else parent_b.min_group_size,
        delta_tol=parent_a.delta_tol if pick_bool() else parent_b.delta_tol,
        max_gap=parent_a.max_gap if pick_bool() else parent_b.max_gap,
        default_categories=dc,
    )
