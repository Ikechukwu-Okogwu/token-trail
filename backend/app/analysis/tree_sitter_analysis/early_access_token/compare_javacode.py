"""
Token-style Java similarity: two strings in, scalar or detailed analysis out.

Strategy: tokenize + k-gram fingerprints (-> ordered sequence).
Shared: Winnow on that sequence, then Jaccard on fingerprint hash sets.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.analysis.tree_sitter_analysis.early_access_token.token_fingerprint import (
    Fingerprint,
    Token,
)


@dataclass(frozen=True)
class JavaCodeSimilarityAnalysis:
    """Full similarity result: score plus Winnow-selected fingerprints per side."""

    similarity: float
    winnowed_fingerprints_a: frozenset[Fingerprint]
    winnowed_fingerprints_b: frozenset[Fingerprint]


@runtime_checkable
class JavaKgramStrategy(Protocol):
    """Tokenization policy + k-gram fingerprints from a pre-built token stream."""

    def tokens_for_kgram(self, code: str) -> Sequence[Token]:
        """Filtered token sequence used for k-grams (indices match ``Fingerprint.token_start_index``)."""
        ...

    def compute_kgram_fingerprints(self, tokens: Sequence[Token]) -> Sequence[Fingerprint]:
        """Ordered k-gram fingerprints from ``tokens`` (before Winnow)."""
        ...


class UnimplementedJavaKgramStrategy:
    """Placeholder until a real tokenize + k-gram implementation exists."""

    def tokens_for_kgram(self, code: str) -> Sequence[Token]:
        raise NotImplementedError(
            "Replace with a strategy that implements tokens_for_kgram + compute_kgram_fingerprints."
        )

    def compute_kgram_fingerprints(self, tokens: Sequence[Token]) -> Sequence[Fingerprint]:
        raise NotImplementedError(
            "Replace with a strategy that implements tokens_for_kgram + compute_kgram_fingerprints."
        )


def winnow_select(seq: Sequence[Fingerprint], window: int) -> frozenset[Fingerprint]:
    """
    Winnow on the k-gram fingerprint sequence (DEFINITION 1: minimum hash per
    window; tie-break: rightmost minimum via (hash_value, -index)).

    Deduplicates by hash_value so Jaccard semantics match hash-only Winnow sets.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    items = list(seq)
    if not items:
        return frozenset()

    indexed = list(enumerate(items))
    n = len(indexed)

    def iter_windows() -> list[list[tuple[int, Fingerprint]]]:
        if n < window:
            return [indexed]
        return [indexed[i : i + window] for i in range(n - window + 1)]

    seen_hashes: set[int] = set()
    reps: list[Fingerprint] = []
    for win in iter_windows():
        _idx, fp = min(win, key=lambda t: (t[1].hash_value, -t[0]))
        if fp.hash_value not in seen_hashes:
            seen_hashes.add(fp.hash_value)
            reps.append(fp)
    return frozenset(reps)


def pairwise_set_similarity(hashes_a: frozenset[int], hashes_b: frozenset[int]) -> float:
    """Jaccard on hash sets; swap later if you need another metric."""
    if not hashes_a and not hashes_b:
        return 0.0
    inter = len(hashes_a & hashes_b)
    union = len(hashes_a | hashes_b)
    return float(inter) / float(union) if union else 0.0


def analyze_java_code_similarity(
    code_a: str,
    code_b: str,
    *,
    strategy: JavaKgramStrategy,
    winnow_window: int = 4,
) -> JavaCodeSimilarityAnalysis:
    """
    k-gram fingerprints from strategy -> Winnow -> Jaccard on hash sets.

    Returns scores and the Winnow-selected fingerprint sets for evidence / APIs.
    """
    if not code_a.strip() or not code_b.strip():
        return JavaCodeSimilarityAnalysis(
            similarity=0.0,
            winnowed_fingerprints_a=frozenset(),
            winnowed_fingerprints_b=frozenset(),
        )
    tok_a = list(strategy.tokens_for_kgram(code_a))
    tok_b = list(strategy.tokens_for_kgram(code_b))
    fp_a = list(strategy.compute_kgram_fingerprints(tok_a))
    fp_b = list(strategy.compute_kgram_fingerprints(tok_b))
    win_a = winnow_select(fp_a, winnow_window)
    win_b = winnow_select(fp_b, winnow_window)
    hashes_a = frozenset(f.hash_value for f in win_a)
    hashes_b = frozenset(f.hash_value for f in win_b)
    sim = pairwise_set_similarity(hashes_a, hashes_b)
    return JavaCodeSimilarityAnalysis(
        similarity=sim,
        winnowed_fingerprints_a=win_a,
        winnowed_fingerprints_b=win_b,
    )


def compare_java_code(
    code_a: str,
    code_b: str,
    *,
    strategy: JavaKgramStrategy,
    winnow_window: int = 4,
) -> float:
    """Wrapper returning only the scalar similarity for batch / legacy callers."""
    return analyze_java_code_similarity(
        code_a,
        code_b,
        strategy=strategy,
        winnow_window=winnow_window,
    ).similarity
