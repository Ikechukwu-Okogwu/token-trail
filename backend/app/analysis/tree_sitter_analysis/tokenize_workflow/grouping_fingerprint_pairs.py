"""
Group fingerprint match pairs into diagonal-like segments.

Mirrors ``testWinowingCode/fingerprint.py`` ``group_match_points`` on
``FingerprintPair`` (pos_a, pos_b, delta). No dependency on how pairs were built.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.analysis.tree_sitter_analysis.tokenize_workflow.fingerprint_pairing import (
    FingerprintPair,
)


@dataclass(frozen=True)
class FingerprintPairGroup:
    """One contiguous chain of ``FingerprintPair`` under the Winnow grouping heuristic."""

    pairs: tuple[FingerprintPair, ...]

    @property
    def pos_a_start(self) -> int:
        return min(p.pos_a for p in self.pairs)

    @property
    def pos_a_end(self) -> int:
        return max(p.pos_a for p in self.pairs)

    @property
    def pos_b_start(self) -> int:
        return min(p.pos_b for p in self.pairs)

    @property
    def pos_b_end(self) -> int:
        return max(p.pos_b for p in self.pairs)



def grouping_fingerprint_pairs(
    points: Sequence[FingerprintPair],
    *,
    min_group_size: int = 4,
    delta_tol: int = 5,
    max_gap: int = 120,
) -> list[FingerprintPairGroup]:
    """
    Same rules as ``group_match_points``:

    - sort by (delta, pos_a, pos_b)
    - extend chain if |Δdelta| <= tol, both coords non-decreasing, both steps <= max_gap
    - keep groups with len >= min_group_size
    """
    if not points:
        return []

    pts = sorted(points, key=lambda p: (p.delta, p.pos_a, p.pos_b))
    raw: list[list[FingerprintPair]] = []
    cur: list[FingerprintPair] = []

    for p in pts:
        if not cur:
            cur = [p]
            continue

        prev = cur[-1]
        same_diag = abs(p.delta - prev.delta) <= delta_tol
        increasing = p.pos_a >= prev.pos_a and p.pos_b >= prev.pos_b
        close_enough = (p.pos_a - prev.pos_a) <= max_gap and (p.pos_b - prev.pos_b) <= max_gap

        if same_diag and increasing and close_enough:
            cur.append(p)
        else:
            if len(cur) >= min_group_size:
                raw.append(cur)
            cur = [p]

    if len(cur) >= min_group_size:
        raw.append(cur)

    raw.sort(key=lambda g: (-len(g), min(x.pos_a for x in g)))
    return [FingerprintPairGroup(pairs=tuple(g)) for g in raw]
