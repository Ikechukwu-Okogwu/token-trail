"""
Turn kept fingerprint groups into token-level “dye” coverage and a file-pair score.

``similarity`` = (marked tokens on A + marked tokens on B) / (|A| + |B|), using the
same inclusive span bounds as :func:`group_analysis.group_token_span_bounds`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.analysis.tree_sitter_analysis.early_access_token.group_analysis import (
    group_token_span_bounds,
)
from app.analysis.tree_sitter_analysis.early_access_token.grouping_fingerprint_pairs import (
    FingerprintPairGroup,
)


@dataclass(frozen=True)
class DyeResult:
    """Result of dyeing token indices covered by the given groups."""

    similarity: float
    marked_count_a: int
    marked_count_b: int
    n_tokens_a: int
    n_tokens_b: int
    dyed_a: tuple[bool, ...]
    dyed_b: tuple[bool, ...]


def dye_tokens(
    groups: Sequence[FingerprintPairGroup],
    *,
    n_tokens_a: int,
    n_tokens_b: int,
    k: int,
) -> DyeResult:
    """
    Mark every token index that lies in the k-gram-covered span of at least one group
    on each side (union). Empty token stream on either side raises ``ValueError``.
    """
    if n_tokens_a <= 0 or n_tokens_b <= 0:
        raise ValueError(
            "dye_tokens: both sides must have at least one token "
            f"(got n_tokens_a={n_tokens_a}, n_tokens_b={n_tokens_b})"
        )

    dyed_a = bytearray(n_tokens_a)
    dyed_b = bytearray(n_tokens_b)

    for g in groups:
        lo_a, hi_a = group_token_span_bounds(g, side="a", k=k, n_tokens=n_tokens_a)
        lo_b, hi_b = group_token_span_bounds(g, side="b", k=k, n_tokens=n_tokens_b)
        if hi_a >= lo_a:
            dyed_a[lo_a : hi_a + 1] = b"\x01" * (hi_a - lo_a + 1)
        if hi_b >= lo_b:
            dyed_b[lo_b : hi_b + 1] = b"\x01" * (hi_b - lo_b + 1)

    ma = int(sum(dyed_a))
    mb = int(sum(dyed_b))
    denom = n_tokens_a + n_tokens_b
    sim = (ma + mb) / denom

    return DyeResult(
        similarity=sim,
        marked_count_a=ma,
        marked_count_b=mb,
        n_tokens_a=n_tokens_a,
        n_tokens_b=n_tokens_b,
        dyed_a=tuple(bool(x) for x in dyed_a),
        dyed_b=tuple(bool(x) for x in dyed_b),
    )
