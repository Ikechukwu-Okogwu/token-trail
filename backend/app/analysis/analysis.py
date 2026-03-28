"""Unified analysis API for external consumers.

Provides language-specific similarity functions. Use these instead of
importing from testWinowingCode directly.
"""

from __future__ import annotations

import sys
from pathlib import Path


def compute_javacode_similarity_archive(
    text_a: str,
    text_b: str,
    template: str = "",
    *,
    k: int = 5,
    name_a: str = "",
    name_b: str = "",
    auto_store: bool = False,
) -> float:
    """Archived: per-class tree-sitter pairing + Winnow mean (see :func:`compute_javacode_similarity`).

    ``template``, ``k``, ``name_a``, ``name_b``, ``auto_store`` are accepted;
    only ``template`` affects behavior (class pairing / exclusion).

    Java only.
    """
    _ = (k, name_a, name_b, auto_store)
    _backend = Path(__file__).resolve().parents[2]
    if str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from app.analysis.tree_sitter_analysis import compute_similarity_javacode

    return compute_similarity_javacode(text_a, text_b, template)


def compute_javacode_similarity(
    text_a: str,
    text_b: str,
    template: str = "",
    *,
    k: int = 5,
    name_a: str = "",
    name_b: str = "",
    auto_store: bool = False,
) -> float:
    """Compute similarity between two Java code strings (0.0 to 1.0).

    Leaf-token pipeline: Winnow k-gram pairing, grouping, type-config filter, then
    dye coverage ``(marked_a + marked_b) / (n_a + n_b)``.

    ``template``, ``name_a``, ``name_b``, ``auto_store`` are accepted for signature
    compatibility but **ignored** (no class-level template exclusion).

    Raises:
        ValueError: empty/whitespace-only input or no leaf tokens on a side.

    Java only.
    """
    _ = (template, name_a, name_b, auto_store)
    _backend = Path(__file__).resolve().parents[2]
    if str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from app.analysis.tree_sitter_analysis.early_access_token.json_kgram_strategy import (
        JsonLeafKgramStrategy,
    )
    from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
        run_tokenize_similarity_pipeline,
    )

    result = run_tokenize_similarity_pipeline(
        text_a,
        text_b,
        strategy=JsonLeafKgramStrategy(k=k),
    )
    return float(result.similarity)
