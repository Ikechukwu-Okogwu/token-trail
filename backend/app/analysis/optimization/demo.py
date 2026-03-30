"""Optimization demos: regression fitness, mutation + bundle save."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.analysis.config import (
    load_active_tokenize_pipeline_config,
    save_tokenize_pipeline_bundle,
)
from app.analysis.optimization.fitness import evaluate_fitness, fitness_from_rows, row_penalty
from app.analysis.optimization.mutation import load_mutation_config, mutate_pipeline_config
from app.analysis.tree_sitter_analysis.demo import run_regression_tests

_OPTIM_ROOT = Path(__file__).resolve().parent


def main_fitness() -> None:
    cfg = load_active_tokenize_pipeline_config()
    print("Active bundle -> regression rows (silence=True)...")
    rows = run_regression_tests(config=cfg, silence=True)
    lam = 0.25
    bd = fitness_from_rows(rows, penalty_weight=lam)
    print(f"n={bd.n}  accuracy={bd.accuracy:.4f}  penalty_mean={bd.penalty_mean:.4f}  lambda={lam}")
    print(f"F = accuracy - lambda*penalty = {bd.fitness:.4f}")

    bd2 = evaluate_fitness(cfg, penalty_weight=lam, silence=True)
    assert abs(bd2.fitness - bd.fitness) < 1e-9

    if rows:
        worst = max(rows, key=lambda r: row_penalty(r))
        print(
            f"highest row penalty: {worst[0]} vs {worst[1]}  "
            f"pass={worst[3]}  penalty={row_penalty(worst):.4f}"
        )


def _fmt_intervals(iv: dict[str, tuple[float, float]]) -> str:
    parts = [f"{k}:[{lo:.3f},{hi:.3f}]" for k, (lo, hi) in sorted(iv.items())]
    return "  " + "; ".join(parts[:4]) + (" ..." if len(parts) > 4 else "")


def demo_mutation_bundle() -> None:
    """Load active config, mutate with default ``mutation_config.json``, print diff, save under ``genes/test_bundle``."""
    before = load_active_tokenize_pipeline_config()
    mc = load_mutation_config()
    after = mutate_pipeline_config(before, mc)

    print("=== Mutation demo ===")
    print("(policy: optimization/description.md, optimization/mutation_config.json)\n")

    print("[pipeline scalars]")
    for label, a, b in [
        ("k", before.k, after.k),
        ("winnow_window", before.winnow_window, after.winnow_window),
        ("max_pos_each", before.max_pos_each, after.max_pos_each),
        ("min_group_size", before.min_group_size, after.min_group_size),
        ("delta_tol", before.delta_tol, after.delta_tol),
        ("max_gap", before.max_gap, after.max_gap),
    ]:
        mark = " *" if a != b else ""
        print(f"  {label}: {a} -> {b}{mark}")

    print("\n[group filter globals]")
    g0, g1 = before.group_filter_config, after.group_filter_config
    for label, va, vb in [
        ("keep_threshold", g0.keep_threshold, g1.keep_threshold),
        ("default_similarity_no_match", g0.default_similarity_no_match, g1.default_similarity_no_match),
    ]:
        mark = " *" if va != vb else ""
        print(f"  {label}: {va:.6f} -> {vb:.6f}{mark}")

    print(f"\n[features] count: {len(g0.features)} -> {len(g1.features)}")
    n = min(len(g0.features), len(g1.features))
    for i in range(n):
        f0, f1 = g0.features[i], g1.features[i]
        changed = (
            f0.intervals != f1.intervals
            or f0.contribution != f1.contribution
            or f0.weight != f1.weight
            or f0.name != f1.name
        )
        if not changed:
            continue
        print(f"  feature[{i}] name: {f0.name!r} -> {f1.name!r}")
        if f0.intervals != f1.intervals:
            print("    intervals before:", _fmt_intervals(dict(f0.intervals)))
            print("    intervals after :", _fmt_intervals(dict(f1.intervals)))
        if f0.contribution != f1.contribution or f0.weight != f1.weight:
            print(
                f"    contribution {f0.contribution:.4f} -> {f1.contribution:.4f}  |  "
                f"weight {f0.weight:.4f} -> {f1.weight:.4f}"
            )
    if len(g1.features) > len(g0.features):
        for j in range(len(g0.features), len(g1.features)):
            fj = g1.features[j]
            print(f"  feature[{j}] NEW: {fj.name!r} weight={fj.weight:.4f}")

    out_dir = _OPTIM_ROOT / "genes" / "test_bundle"
    meta = save_tokenize_pipeline_bundle(after, out_dir)
    print(f"\nSaved mutated bundle to: {meta.parent.resolve()}")
    print(f"meta.json: {meta.resolve()}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Optimization module demos.")
    sp = ap.add_subparsers(dest="cmd")
    sp.add_parser("fitness", help="Regression fitness on the active bundle (slow).")
    sp.add_parser(
        "mutate",
        help="Mutate active config, print before/after, save to optimization/genes/test_bundle.",
    )
    ns = ap.parse_args()
    if ns.cmd == "mutate":
        demo_mutation_bundle()
    else:
        main_fitness()


if __name__ == "__main__":
    main()
