"""Unified analysis API for external consumers.

Provides language-specific similarity functions. Use these instead of
importing from testWinowingCode directly.
"""

from __future__ import annotations

import sys
from pathlib import Path


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

    Signature matches compare_texts_with_template for drop-in replacement.
    template, k, name_a, name_b, auto_store are accepted but unused.

    Uses tree-sitter for function pairing and variable normalization,
    then Winnowing for fingerprint-based similarity per pair.
    Returns the mean of pairwise similarities; 0.0 if no pairs.

    Java only. For other languages, use testWinowingLib.compare_texts_with_template.
    """
    _backend = Path(__file__).resolve().parents[2]
    if str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from app.analysis.tree_sitter_analysis import compute_similarity_javacode
    return compute_similarity_javacode(text_a, text_b)
