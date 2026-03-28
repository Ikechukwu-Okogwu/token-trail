"""
Pair Winnow fingerprints between two Java sources (testWinowing-style ``build_match_points``).

Uses ``token_start_index`` as ``pos_a`` / ``pos_b``. Winnow step keeps **every** window
selection (duplicate ``hash_value`` at different positions), unlike ``winnow_select``
which dedupes for Jaccard.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from app.analysis.tree_sitter_analysis.early_access_token.token_fingerprint import (
    Fingerprint,
)


@dataclass(frozen=True)
class FingerprintPair:
    """One hash match: k-gram start index on A vs B (filtered token stream)."""

    pos_a: int
    pos_b: int
    hash_value: int

    @property
    def index_delta(self) -> int:
        """Same as ``MatchPoint.delta`` in testWinowingCode: pos_b - pos_a."""
        return self.pos_b - self.pos_a

    @property
    def delta(self) -> int:
        return self.index_delta


def winnow_fingerprint_sequence(seq: Sequence[Fingerprint], window: int) -> list[Fingerprint]:
    """
    Winnow (DEFINITION 1): one selected fingerprint per window, **no hash dedup**.

    Needed so ``hash -> [pos, ...]`` can list multiple positions like ``fingerprint_index``.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    items = list(seq)
    if not items:
        return []

    indexed = list(enumerate(items))
    n = len(indexed)

    def iter_windows() -> list[list[tuple[int, Fingerprint]]]:
        if n < window:
            return [indexed]
        return [indexed[i : i + window] for i in range(n - window + 1)]

    out: list[Fingerprint] = []
    for win in iter_windows():
        _idx, fp = min(win, key=lambda t: (t[1].hash_value, -t[0]))
        out.append(fp)
    return out


def fingerprint_hash_to_positions(
    fps: Sequence[Fingerprint],
) -> dict[int, list[int]]:
    """
    ``hash_value -> sorted token_start_index list`` (testWinowing ``fingerprint_index``).

    Each ``(hash_value, token_start_index)`` is counted once: Winnow may pick the same
    k-gram in multiple windows, but indexing for pairing matches unique positions per hash.
    """
    tmp: dict[int, set[int]] = defaultdict(set)
    for f in fps:
        tmp[f.hash_value].add(f.token_start_index)
    return {h: sorted(xs) for h, xs in tmp.items()}


def pairing_fingerprints(
    index_a: Mapping[int, Sequence[int]],
    index_b: Mapping[int, Sequence[int]],
    common_hashes: Iterable[int],
    *,
    max_pos_each: int = 100,
) -> list[FingerprintPair]:
    """
    Cartesian pairing per common hash, capped by ``max_pos_each`` per side
    (same idea as ``build_match_points``).
    """
    points: list[FingerprintPair] = []
    for hs in common_hashes:
        if hs not in index_a or hs not in index_b:
            continue
        pos_a_list = list(index_a[hs])[:max_pos_each]
        pos_b_list = list(index_b[hs])[:max_pos_each]
        for pa in pos_a_list:
            for pb in pos_b_list:
                points.append(
                    FingerprintPair(pos_a=pa, pos_b=pb, hash_value=hs)
                )
    return points


def pairing_list_from_winnow_fingerprint_sequences(
    winnowed_a: Sequence[Fingerprint],
    winnowed_b: Sequence[Fingerprint],
    *,
    max_pos_each: int = 100,
) -> list[FingerprintPair]:
    """
    Build Cartesian match pairs from Winnow **sequence** outputs per side (see
    ``winnow_fingerprint_sequence``): hash -> positions, then ``pairing_fingerprints``.

    Caller runs strategy -> raw k-gram list -> Winnow; this module does not take source
    text or a strategy.
    """
    if not winnowed_a or not winnowed_b:
        return []
    index_a = fingerprint_hash_to_positions(winnowed_a)
    index_b = fingerprint_hash_to_positions(winnowed_b)
    common_hashes = set(index_a.keys()) & set(index_b.keys())
    return pairing_fingerprints(
        index_a,
        index_b,
        common_hashes,
        max_pos_each=max_pos_each,
    )
