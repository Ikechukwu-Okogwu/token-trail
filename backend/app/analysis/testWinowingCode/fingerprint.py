# -*- coding: utf-8 -*-
"""
Fingerprint data structure and winnow wrapper.

Provides Fingerprint and MatchPoint as canonical representations.
Includes fingerprint indexing, match point construction, and grouping.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

try:
    from .winnowingCopy import winnow as _raw_winnow
except ImportError:  # pragma: no cover
    from winnowingCopy import winnow as _raw_winnow


@dataclass(frozen=True)
class Fingerprint:
    """A single fingerprint in a document: position in original text + hash value."""

    position: int
    hash_val: int
    shared_in_template: bool = False


@dataclass(frozen=True)
class MatchPoint:
    """
    A match point: the same fingerprint hash at pos_a in file A and pos_b in file B.
    delta = pos_b - pos_a (used for grouping diagonal-like segments).
    """

    pos_a: int
    pos_b: int
    hash_val: int
    delta: int


def winnow(text: str, k: int = 5) -> set[Fingerprint]:
    """
    Compute document fingerprints via winnowing.

    Delegates to winnowingCopy.winnow, wrapping results as Fingerprint objects.
    Returns a set of Fingerprint; shared_in_template is False by default.
    """
    raw = _raw_winnow(text, k=k)
    return {Fingerprint(position=p, hash_val=h) for p, h in raw}


def fingerprint_hashes(fingerprints: Iterable[Fingerprint]) -> set[int]:
    """Extract hash values from Fingerprint objects."""
    return {f.hash_val for f in fingerprints}


def fingerprint_index(fingerprints: Iterable[Fingerprint]) -> defaultdict[int, list[int]]:
    """Build hash -> [positions] index from Fingerprint objects."""
    index = defaultdict(list)
    for f in fingerprints:
        index[f.hash_val].append(f.position)
    for hs in index:
        index[hs].sort()
    return index

# def mark_all_points_as_shared_in_template(points: list[MatchPoint]):
#     """Mark all points as shared in template."""
#     for point in points:
#         point.shared_in_template = True
#     return points

def build_match_points(
    index_a: dict[int, list[int]],
    index_b: dict[int, list[int]],
    common_hashes: Iterable[int],
    max_pos_each: int = 10,
) -> list[MatchPoint]:
    """
    Build match points between two files from common hashes.

    Returns a list of MatchPoint. To avoid combinatorial explosion, we only use
    up to max_pos_each positions per hash on each side.
    """
    points = []
    for hs in common_hashes:
        count_a = len(index_a[hs])
        count_b = len(index_b[hs])
        if count_a > max_pos_each or count_b > max_pos_each:
            print(
                f"[CUT] hash={hs}  occurrences: A={count_a}, B={count_b}  "
                f"(max_pos_each={max_pos_each})"
            )

        pos_a_list = index_a[hs][:max_pos_each]
        pos_b_list = index_b[hs][:max_pos_each]
        for pa in pos_a_list:
            for pb in pos_b_list:
                points.append(MatchPoint(pos_a=pa, pos_b=pb, hash_val=hs, delta=pb - pa))
    return points


def group_match_points(
    points: Sequence[MatchPoint],
    min_group_size: int = 4,
    delta_tol: int = 5,
    max_gap: int = 120,
) -> list[list[MatchPoint]]:
    """
    Group match points into "continuous" diagonal-like segments.

    Heuristic: points in the same group should
    - have similar delta (pos_b - pos_a)
    - be increasing in both pos_a and pos_b
    - not jump too far between consecutive points
    """
    if not points:
        return []

    pts = sorted(points, key=lambda p: (p.delta, p.pos_a, p.pos_b))
    groups = []
    cur = []

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
                groups.append(cur)
            cur = [p]

    if len(cur) >= min_group_size:
        groups.append(cur)

    groups.sort(key=lambda g: (-len(g), min(x.pos_a for x in g)))
    return groups
