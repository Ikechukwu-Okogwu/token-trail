# -*- coding: utf-8 -*-
"""
Render compare results to HTML with highlights.

This module is intentionally independent from the compare logic.
"""

from __future__ import annotations

import os
import random
from collections import defaultdict
from html import escape
from typing import Sequence

try:
    from .fingerprint import MatchPoint
except ImportError:  # pragma: no cover
    from fingerprint import MatchPoint


def _random_pastel_hex() -> str:
    """Generate a readable random pastel background color."""
    r = random.randint(160, 240)
    g = random.randint(160, 240)
    b = random.randint(160, 240)
    return f"#{r:02x}{g:02x}{b:02x}"


def _apply_group_highlight_html(text: str, intervals, group_colors) -> str:
    """
    Wrap intervals with <span style="background: ...">[i]...</span>.

    intervals: list of (start, end, group_id), start/end inclusive, in original text offsets.
    group_colors: dict[int, str] mapping group_id -> css color

    Notes:
    - Only adds a textual marker at the *start* of each interval: "[i]".
    - Overlapping intervals are clipped to avoid invalid nesting.
    - Escapes HTML in the original text.
    """
    if not intervals:
        return escape(text)

    intervals_sorted = sorted(intervals, key=lambda t: (t[0], t[1], t[2]))
    clipped = []
    last_end = -1
    for start, end, gid in intervals_sorted:
        start = max(0, start)
        end = min(len(text) - 1, end)
        if start <= last_end:
            start = last_end + 1
        if start > end:
            continue
        clipped.append((start, end, gid))
        last_end = end

    # events[pos] = {"close": [...], "open": [...]}
    events: dict[int, dict[str, list[str]]] = defaultdict(lambda: {"close": [], "open": []})
    for start, end, gid in clipped:
        color = group_colors.get(gid, "#ffff99")
        # Only mark start with "[gid]" inside the highlight.
        events[start]["open"].append(
            f'<span class="sim" style="background:{color}"><span class="tag">[{gid}]</span>'
        )
        events[end + 1]["close"].append("</span>")

    out = []
    cursor = 0
    boundaries = sorted(set([0, len(text)] + list(events.keys())))
    for b in boundaries:
        if b < cursor:
            continue
        if cursor < b:
            out.append(escape(text[cursor:b]))
        if b in events:
            out.extend(events[b]["close"])
            out.extend(events[b]["open"])
        cursor = b

    return "".join(out)


def _ensure_html_header(path: str, title: str) -> None:
    """Create an HTML file with header if it doesn't exist or is empty."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            "<!doctype html>\n"
            "<html>\n<head>\n"
            '  <meta charset="utf-8" />\n'
            f"  <title>{escape(title)}</title>\n"
            "  <style>\n"
            "    body { font-family: system-ui, -apple-system, Segoe UI, Arial, sans-serif; margin: 16px; }\n"
            "    pre.code { white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; "
            "font-size: 12px; line-height: 1.4; padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin: 0; }\n"
            "    .sim { border-radius: 3px; padding: 0 1px; }\n"
            "    .tag { font-weight: 700; margin-right: 4px; }\n"
            "    hr { border: 0; border-top: 1px solid #ddd; margin: 18px 0; }\n"
            "    .meta { color: #444; margin: 6px 0 12px; }\n"
            "    .split { display: flex; gap: 16px; align-items: flex-start; }\n"
            "    .split > div { flex: 1; min-width: 0; overflow-x: auto; }\n"
            "    .split-block { margin-bottom: 24px; }\n"
            "  </style>\n"
            "</head>\n<body>\n"
        )


def store_compare_result_as_html(
    *,
    base_dir: str,
    name_a: str,
    name_b: str,
    text_a: str,
    text_b: str,
    similarity: float,
    overlap: int,
    groups: Sequence[Sequence[MatchPoint]],
) -> None:
    """
    Store grouped compare result into result.html with left/right split view.
    Each call appends a block; multiple blocks are stacked vertically.

    For each group i (1-based), highlight the corresponding region and add a start tag "[i]".
    Colors are randomized but consistent per group across both sides.
    """
    out_path = os.path.join(base_dir, "result.html")
    _ensure_html_header(out_path, "Similarity result")

    group_colors = {gid: _random_pastel_hex() for gid in range(1, len(groups) + 1)}

    intervals_a = []
    intervals_b = []
    for gid, g in enumerate(groups, start=1):
        a_start = min(x.pos_a for x in g)
        a_end = max(x.pos_a for x in g)
        b_start = min(x.pos_b for x in g)
        b_end = max(x.pos_b for x in g)
        intervals_a.append((a_start, a_end, gid))
        intervals_b.append((b_start, b_end, gid))

    annotated_a = _apply_group_highlight_html(text_a, intervals_a, group_colors)
    annotated_b = _apply_group_highlight_html(text_b, intervals_b, group_colors)

    meta_html = (
        f"<h2>{escape(f'Winnowing test ({name_a} vs {name_b})')}</h2>\n"
        f'<div class="meta">Overlap: <b>{overlap}</b> &nbsp; '
        f"Jaccard similarity: <b>{similarity:.2%}</b> &nbsp; "
        f"Groups: <b>{len(groups)}</b></div>\n"
    )

    block_html = (
        '<div class="split-block">\n'
        f"  {meta_html}"
        '  <div class="split">\n'
        '    <div><pre class="code">'
        + annotated_a
        + "</pre></div>\n"
        '    <div><pre class="code">'
        + annotated_b
        + "</pre></div>\n"
        "  </div>\n"
        "</div>\n<hr/>\n"
    )

    with open(out_path, "a", encoding="utf-8") as f:
        f.write(block_html)

