"""Tests for feature-interval crossover (one-to-one greedy pairing)."""

from __future__ import annotations

import random
import unittest

from app.analysis.config import load_active_tokenize_pipeline_config
from app.analysis.optimization.crossover import (
    crossover_group_filter_config,
    crossover_pipeline_config,
    load_crossover_config,
    _greedy_pairs,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    GroupFilterConfig,
    GroupFilterFeature,
)


def _feat(
    name: str,
    keys: dict[str, tuple[float, float]],
    *,
    role: str = "evidence_positive",
    contribution: float = 0.7,
    weight: float = 1.0,
) -> GroupFilterFeature:
    return GroupFilterFeature(
        name=name,
        intervals=dict(keys),
        contribution=contribution,
        weight=weight,
        role=role,
    )


def _cfg(
    *feats: GroupFilterFeature,
    keep: float = 0.5,
    default_sim: float = 0.5,
) -> GroupFilterConfig:
    return GroupFilterConfig(
        keep_threshold=keep,
        default_similarity_no_match=default_sim,
        features=tuple(feats),
    )


class CrossoverGroupFilterTests(unittest.TestCase):
    def test_matched_child_has_union_keys(self) -> None:
        fa = _feat("a", {"literal": (0.0, 0.5), "punct": (0.2, 0.4)})
        fb = _feat("b", {"literal": (0.1, 0.6), "name": (0.0, 0.3)})
        ga = _cfg(fa)
        gb = _cfg(fb)
        rng = random.Random(1)
        xcfg = {
            "prob_keep_unmatched_feature": 0.0,
            "require_same_role_for_pairing": True,
            "min_overlap_keys": 1,
        }
        child = crossover_group_filter_config(ga, gb, rng, xcfg)
        self.assertEqual(len(child.features), 1)
        c0 = child.features[0]
        self.assertEqual(set(c0.intervals.keys()), {"literal", "punct", "name"})
        self.assertIn("_x_", c0.name)

    def test_interval_values_come_from_either_parent(self) -> None:
        fa = _feat("a", {"k": (0.1, 0.2)})
        fb = _feat("b", {"k": (0.8, 0.9)})
        ga, gb = _cfg(fa), _cfg(fb)
        rng = random.Random(0)
        child = crossover_group_filter_config(
            ga, gb, rng, {"prob_keep_unmatched_feature": 0.0, "min_overlap_keys": 1}
        )
        iv = child.features[0].intervals["k"]
        self.assertIn(iv, {(0.1, 0.2), (0.8, 0.9)})

    def test_one_to_one_only_one_anchor_gets_shared_donor(self) -> None:
        donor = _feat("d", {"literal": (0.0, 1.0)})
        f1 = _feat("f1", {"literal": (0.2, 0.4)})
        f2 = _feat("f2", {"literal": (0.3, 0.5)})
        ga = _cfg(f1, f2)
        gb = _cfg(donor)
        rng = random.Random(123)
        xcfg = {"prob_keep_unmatched_feature": 0.0, "min_overlap_keys": 1}
        child = crossover_group_filter_config(ga, gb, rng, xcfg)
        crossed = [f for f in child.features if "_x_" in f.name]
        self.assertEqual(len(crossed), 1)

    def test_role_gate_no_pair_when_roles_differ(self) -> None:
        fa = _feat("a", {"x": (0.0, 1.0)}, role="r_a")
        fb = _feat("b", {"x": (0.0, 1.0)}, role="r_b")
        ga, gb = _cfg(fa), _cfg(fb)
        rng = random.Random(0)
        child = crossover_group_filter_config(
            ga,
            gb,
            rng,
            {
                "prob_keep_unmatched_feature": 0.0,
                "require_same_role_for_pairing": True,
                "min_overlap_keys": 1,
            },
        )
        self.assertEqual(len(child.features), 0)

    def test_unmatched_all_kept_when_prob_one(self) -> None:
        fa = _feat("only_a", {"a": (0.0, 1.0)})
        fb = _feat("only_b", {"b": (0.0, 1.0)})
        ga, gb = _cfg(fa), _cfg(fb)
        rng = random.Random(0)
        child = crossover_group_filter_config(
            ga,
            gb,
            rng,
            {
                "prob_keep_unmatched_feature": 1.0,
                "require_same_role_for_pairing": True,
                "min_overlap_keys": 99,
            },
        )
        names = {f.name for f in child.features}
        self.assertEqual(names, {"only_a", "only_b"})

    def test_all_weights_positive(self) -> None:
        a = load_active_tokenize_pipeline_config()
        b = load_active_tokenize_pipeline_config()
        rng = random.Random(42)
        c = crossover_pipeline_config(a, b, rng=rng)
        for f in c.group_filter_config.features:
            self.assertGreater(f.weight, 0.0)


class GreedyPairsTests(unittest.TestCase):
    def test_greedy_prefers_larger_overlap(self) -> None:
        donor_big = _feat("big", {"a": (0.0, 1.0), "b": (0.0, 1.0), "c": (0.0, 1.0)})
        donor_small = _feat("small", {"a": (0.0, 1.0)})
        anchor = _feat("anchor", {"a": (0.0, 1.0), "b": (0.0, 1.0)})
        anchors = [anchor]
        donors = [donor_small, donor_big]
        rng = random.Random(0)
        pairs = _greedy_pairs(anchors, donors, rng, {"min_overlap_keys": 1})
        paired = pairs[0][1]
        self.assertIsNotNone(paired)
        assert paired is not None
        self.assertEqual(paired.name, "big")


class CrossoverConfigTests(unittest.TestCase):
    def test_load_default_json(self) -> None:
        d = load_crossover_config()
        self.assertIn("prob_keep_unmatched_feature", d)
        self.assertIn("require_same_role_for_pairing", d)


if __name__ == "__main__":
    unittest.main()
