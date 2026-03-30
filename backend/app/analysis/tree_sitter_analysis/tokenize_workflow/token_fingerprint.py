"""
Core record types for leaf-token similarity (plan: token vs fingerprint layers).

Token: syntax leaf + byte span + 1-based line span.
Fingerprint: one k-gram hash + source span + token index range + line span.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass


def byte_span_to_one_based_lines(
    source: bytes, start_byte: int, end_byte: int
) -> tuple[int, int]:
    """
    Map half-open byte range [start_byte, end_byte) to inclusive 1-based
    (start_line, end_line). Empty span uses line 1.
    """
    if end_byte <= start_byte:
        line = source[: start_byte if start_byte > 0 else 0].count(b"\n") + 1
        return (line, line)
    start_line = source[:start_byte].count(b"\n") + 1
    end_line = source[:end_byte].count(b"\n") + 1
    return (start_line, end_line)


def slice_text(one: Token, other: Token, original_str: str) -> str:
    """
    Smallest UTF-8 byte span covering both tokens: half-open [lo, hi) in ``original_str``
    encoded as UTF-8 (same convention as Tree-sitter ``start_byte`` / ``end_byte``).
    """
    lo = min(one.start_byte, other.start_byte)
    hi = max(one.end_byte, other.end_byte)
    if hi <= lo:
        return ""
    raw = original_str.encode("utf-8")
    lo = max(0, min(lo, len(raw)))
    hi = max(lo, min(hi, len(raw)))
    return raw[lo:hi].decode("utf-8", errors="replace")


@dataclass(frozen=True)
class Token:
    """One syntactic leaf from the Tree-sitter Java tree."""

    type: str
    text: str
    start_byte: int
    end_byte: int
    start_line: int
    end_line: int


def _categories_for_raw_type(
    raw_type: str,
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str],
) -> frozenset[str]:
    if raw_type in type_mapping:
        cats = frozenset(type_mapping[raw_type])
        if cats:
            return cats
    return frozenset(default_categories)


def mapped_category_columns(
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str] = ("unmapped",),
) -> list[str]:
    """Stable sorted union of all mapped labels plus defaults."""
    s: set[str] = set(default_categories)
    for v in type_mapping.values():
        s.update(v)
    return sorted(s)


def mapped_type_truth_table(
    tokens: Sequence[Token],
    type_mapping: Mapping[str, Collection[str]],
    *,
    default_categories: Collection[str] = ("unmapped",),
    columns: Collection[str] | None = None,
):
    """
    Boolean matrix: row index = token index in ``tokens``, column = mapped category.

    A token row has ``True`` in **every** column it maps to (multi-label). Row sums can
    exceed 1; span **mass** = sum of booleans in the slice (matches ``group_analysis``
    mass accounting).
    """
    import numpy as np
    import pandas as pd

    cols = (
        list(columns)
        if columns is not None
        else mapped_category_columns(type_mapping, default_categories=default_categories)
    )
    cat_index = {c: j for j, c in enumerate(cols)}
    n = len(tokens)
    if n == 0:
        return pd.DataFrame(columns=cols, dtype=bool)
    mat = np.zeros((n, len(cols)), dtype=bool)
    for i, tok in enumerate(tokens):
        for c in _categories_for_raw_type(
            tok.type, type_mapping, default_categories=default_categories
        ):
            j = cat_index.get(c)
            if j is not None:
                mat[i, j] = True
    return pd.DataFrame(mat, columns=cols, dtype=bool)


def align_mapped_type_truth_tables(df_a, df_b):
    """Union columns; missing entries filled with ``False`` (same schema for A/B)."""
    cols = sorted(set(df_a.columns) | set(df_b.columns))
    if not cols:
        return df_a.copy(), df_b.copy()
    a = df_a.reindex(columns=cols, fill_value=False)
    b = df_b.reindex(columns=cols, fill_value=False)
    return a, b


@dataclass(frozen=True)
class Fingerprint:
    """
    One k-gram fingerprint over a contiguous slice of the token stream.

    ``token_start_index`` / ``token_end_index`` are a half-open range into the
    same token list used to compute ``hash_value`` (often after filtering).
    Byte and line spans cover the full source extent of those tokens.
    """

    hash_value: int
    start_byte: int
    end_byte: int
    token_start_index: int
    token_end_index: int
    start_line: int
    end_line: int
