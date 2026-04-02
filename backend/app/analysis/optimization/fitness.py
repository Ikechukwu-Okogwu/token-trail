"""
Regression fitness for tokenize pipeline configs: ``F = accuracy - λ * penalty``.

``penalty`` is the mean per-row deviation for failing cases (0 for passes); deviation
is distance from the allowed ``[low, high]`` interval, normalized by interval width.
Pipeline errors (``score is None``) count as deviation 1.0.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from app.analysis.config import TokenizePipelineConfig, load_active_tokenize_pipeline_config
from app.analysis.tree_sitter_analysis.demo import RegressionRow, run_regression_tests


def _distance_to_interval(score: float, low: float, high: float) -> float:
    if low > high:
        low, high = high, low
    if score < low:
        return low - score
    if score > high:
        return score - high
    return 0.0


def row_penalty(row: RegressionRow) -> float:
    """Nonnegative penalty for one regression row (0 if pass)."""
    _name_a, _name_b, score, is_pass, _expected, (low, high) = row
    if is_pass:
        return 0.0
    if score is None:
        return 1.0
    dist = _distance_to_interval(score, low, high)
    span = max(high - low, 1e-9)
    return min(dist / span, 10.0)


@dataclass(frozen=True)
class FitnessBreakdown:
    fitness: float
    accuracy: float
    penalty_mean: float
    n: int


def fitness_from_rows(
    rows: Sequence[RegressionRow],
    *,
    penalty_weight: float = 0.25,
) -> FitnessBreakdown:
    """``F = accuracy - penalty_weight * mean(row_penalty)``. Accuracy in [0, 1]."""
    if not rows:
        return FitnessBreakdown(fitness=0.0, accuracy=0.0, penalty_mean=0.0, n=0)
    n = len(rows)
    passed = sum(1 for r in rows if r[3])
    accuracy = passed / n
    penalty_mean = sum(row_penalty(r) for r in rows) / n
    fitness = accuracy - penalty_weight * penalty_mean
    return FitnessBreakdown(
        fitness=fitness,
        accuracy=accuracy,
        penalty_mean=penalty_mean,
        n=n,
    )


def evaluate_fitness(
    config: TokenizePipelineConfig,
    *,
    penalty_weight: float = 0.25,
    fixtures: Sequence[Path] | None = None,
    silence: bool = True,
) -> FitnessBreakdown:
    """Run bundled regression with ``config`` and return ``F`` plus components."""
    rows = run_regression_tests(
        config=config,
        silence=silence,
        fixtures=fixtures,
    )
    return fitness_from_rows(rows, penalty_weight=penalty_weight)


def fitness_scalar(
    config: TokenizePipelineConfig | None = None,
    *,
    penalty_weight: float = 0.25,
    fixtures: Sequence[Path] | None = None,
    silence: bool = True,
) -> float:
    """Convenience: fitness float; ``config`` default = active bundle."""
    cfg = config if config is not None else load_active_tokenize_pipeline_config()
    return evaluate_fitness(
        cfg,
        penalty_weight=penalty_weight,
        fixtures=fixtures,
        silence=silence,
    ).fitness
