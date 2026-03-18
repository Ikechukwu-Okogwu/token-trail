# -*- coding: utf-8 -*-
"""
Test winnowing library: compare two files from similarCodes folder.
Run with project venv: venv\\Scripts\\python.exe testWinowingLib.py
"""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Sequence

# Support both:
# - importing as a package module (used by the backend)
# - running this file directly as a script (original dev workflow)
try:
    from .fingerprint import (
        Fingerprint,
        MatchPoint,
        build_match_points,
        fingerprint_hashes,
        fingerprint_index,
        group_match_points,
        winnow,
    )
except ImportError:  # pragma: no cover
    from fingerprint import (
        Fingerprint,
        MatchPoint,
        build_match_points,
        fingerprint_hashes,
        fingerprint_index,
        group_match_points,
        winnow,
    )


def marked_line_at_offset(text: str, offset: int):
    """
    Return (line_no, marked_line) for a character offset in text.
    The target character position is marked with !!.
    """
    if offset < 0 or offset >= len(text):
        return -1, f"<offset {offset} out of range (len={len(text)})>"

    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)

    line = text[line_start:line_end]
    col = offset - line_start
    line_no = text.count("\n", 0, offset) + 1

    if col < len(line):
        marked = line[:col] + "!!" + line[col : col + 1] + "!!" + line[col + 1 :]
    else:
        # offset points at end-of-line (e.g., newline char); mark insertion point
        marked = line + "!!"

    return line_no, marked


def _apply_group_tags(text: str, intervals):
    """
    Insert <sim group=i>...</sim group=i> tags into text for each interval.

    intervals: list of (start, end, group_id), where start/end are inclusive
    character offsets in the original text.

    Overlapping intervals are clipped to avoid invalid nesting.
    """
    if not intervals:
        return text

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
    events = defaultdict(lambda: {"close": [], "open": []})
    for start, end, gid in clipped:
        events[start]["open"].append(f"<sim group={gid}>")
        events[end + 1]["close"].append(f"</sim group={gid}>")  # end+1 can be len(text)

    out = []
    for i in range(len(text) + 1):
        if i in events:
            out.extend(events[i]["close"])
            out.extend(events[i]["open"])
        if i < len(text):
            out.append(text[i])
    return "".join(out)


def store_compare_result(
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
    Store grouped compare result into two files:
      - original.txt: annotated content for file A
      - compared.txt: annotated content for file B

    For each group i (1-based), wrap the corresponding region with:
      <sim group=i> ... </sim group=i>
    """
    out_a_path = os.path.join(base_dir, "original.txt")
    out_b_path = os.path.join(base_dir, "compared.txt")

    intervals_a = []
    intervals_b = []
    for gid, g in enumerate(groups, start=1):
        a_start = min(x.pos_a for x in g)
        a_end = max(x.pos_a for x in g)
        b_start = min(x.pos_b for x in g)
        b_end = max(x.pos_b for x in g)
        intervals_a.append((a_start, a_end, gid))
        intervals_b.append((b_start, b_end, gid))

    annotated_a = _apply_group_tags(text_a, intervals_a)
    annotated_b = _apply_group_tags(text_b, intervals_b)

    header = (
        f"Winnowing test ({name_a} vs {name_b})\n"
        f"Overlap: {overlap}\n"
        f"Jaccard similarity: {similarity:.2%}\n"
        f"Groups: {len(groups)}\n"
        + ("=" * 70)
        + "\n"
    )

    with open(out_a_path, "a", encoding="utf-8") as fa:
        fa.write(header)
        fa.write(annotated_a)
        if not annotated_a.endswith("\n"):
            fa.write("\n")
        fa.write("\n")

    with open(out_b_path, "a", encoding="utf-8") as fb:
        fb.write(header)
        fb.write(annotated_b)
        if not annotated_b.endswith("\n"):
            fb.write("\n")
        fb.write("\n")


def jaccard_similarity(set_a, set_b):
    """Jaccard similarity: |intersection| / |union|."""
    # Project requirement: empty file vs any file => similarity 0
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def compute_similarity_from_text(text_a: str, text_b: str, *, k: int = 5) -> float:
    """Compute similarity score between two texts (0..1).

    - No printing
    - No file I/O
    - Empty text vs any text => 0
    """
    # print("new implementation")
    result = compare_texts_with_template(text_a, text_b, "", k=k)
    return result["similarity"]


def compare_files(path_a: str, path_b: str) -> dict:
    """Compare two files with winnowing and print similarity."""
    name_a = os.path.basename(path_a)
    name_b = os.path.basename(path_b)

    with open(path_a, "r", encoding="utf-8") as f:
        text_a = f.read()
    with open(path_b, "r", encoding="utf-8") as f:
        text_b = f.read()

    fp_a = winnow(text_a, k=5)
    fp_b = winnow(text_b, k=5)

    index_a = fingerprint_index(fp_a)
    index_b = fingerprint_index(fp_b)

    hashes_a = set(index_a.keys())
    hashes_b = set(index_b.keys())

    similarity = jaccard_similarity(hashes_a, hashes_b)
    common_hashes = hashes_a & hashes_b
    overlap = len(common_hashes)

    print(f"Winnowing test ({name_a} vs {name_b})")
    print("-" * 50)
    print(f"{name_a}: {len(fp_a)} fingerprints, {len(hashes_a)} unique hashes")
    print(f"{name_b}: {len(fp_b)} fingerprints, {len(hashes_b)} unique hashes")
    print(f"Overlap:     {overlap} common hashes")
    print(f"Jaccard similarity: {similarity:.2%}")

    # Grouped report: show continuous match blocks (heuristic)
    points = build_match_points(index_a, index_b, common_hashes, max_pos_each=5) if common_hashes else []
    groups = group_match_points(points, min_group_size=4, delta_tol=5, max_gap=120) if points else []

    # Do not print group details to console; store them to files instead.
    # store_compare_result(
    #     base_dir=os.path.dirname(os.path.abspath(__file__)),
    #     name_a=name_a,
    #     name_b=name_b,
    #     text_a=text_a,
    #     text_b=text_b,
    #     similarity=similarity,
    #     overlap=overlap,
    #     groups=groups,
    # )

    return {
        "base_dir": os.path.dirname(os.path.abspath(__file__)),
        "name_a": name_a,
        "name_b": name_b,
        "text_a": text_a,
        "text_b": text_b,
        "similarity": similarity,
        "overlap": overlap,
        "groups": groups,
        "points": points
    }


def compare_texts_with_template(
    text_a: str, text_b: str, template: str = "", *, k: int = 5, name_a: str = "", name_b: str = ""
) -> dict:
    """Compare two texts with winnowing, optionally excluding template hashes from overlap and similarity.

    If template is empty string, no exclusion is applied.
    """
    if not text_a or not text_b or not text_a.strip() or not text_b.strip():
        return {
            "base_dir": os.path.dirname(os.path.abspath(__file__)),
            "name_a": name_a,
            "name_b": name_b,
            "text_a": text_a,
            "text_b": text_b,
            "similarity": 0.0,
            "overlap": 0,
            "groups": [],
            "points": [],
        }

    fp_a = winnow(text_a, k=k)
    fp_b = winnow(text_b, k=k)
    index_a = fingerprint_index(fp_a)
    index_b = fingerprint_index(fp_b)

    hashes_a = set(index_a.keys())
    hashes_b = set(index_b.keys())

    if template and template.strip():
        fp_template = winnow(template, k=k)
        template_hashes = set(fingerprint_index(fp_template).keys())
        common_hashes = (hashes_a & hashes_b) - template_hashes
        hashes_a_filtered = hashes_a - template_hashes
        hashes_b_filtered = hashes_b - template_hashes
        for h in template_hashes:
            index_a.pop(h, None)
            index_b.pop(h, None)
    else:
        common_hashes = hashes_a & hashes_b
        hashes_a_filtered = hashes_a
        hashes_b_filtered = hashes_b

    similarity = jaccard_similarity(hashes_a_filtered, hashes_b_filtered)
    overlap = len(common_hashes)

    points = build_match_points(index_a, index_b, common_hashes, max_pos_each=100) if common_hashes else []
    groups = group_match_points(points, min_group_size=4, delta_tol=5, max_gap=20) if points else []

    return {
        "base_dir": os.path.dirname(os.path.abspath(__file__)),
        "name_a": name_a,
        "name_b": name_b,
        "text_a": text_a,
        "text_b": text_b,
        "similarity": similarity,
        "overlap": overlap,
        "groups": groups,
        "points": points,
    }



def main():
    base = os.path.dirname(os.path.abspath(__file__))
    # Reset outputs each run
    open(os.path.join(base, "original.txt"), "w", encoding="utf-8").close()
    open(os.path.join(base, "compared.txt"), "w", encoding="utf-8").close()
    similar_codes_dir = os.path.join(base, "similarCodesWithTemplate")
    path_original = os.path.join(similar_codes_dir, "original.py")
    path_changed = os.path.join(similar_codes_dir, "changed.py")
    path_template = os.path.join(similar_codes_dir, "template.py")
    # path_change_var_names = os.path.join(similar_codes_dir, "changeVarNames.py")

    # compare_files(path_original, path_copied)
    # print()
    # compare_files(path_original, path_change_var_names)

    # original_with_template = compare_files(path_original, path_template)
    # changed_with_template = compare_files(path_changed, path_template)
    # original_with_changed = compare_files(path_original, path_changed)


    from render_result import store_compare_result_as_html
    # r1 = compare_files(path_original, path_template)

    with open(path_original, "r", encoding="utf-8") as f:
        text_original = f.read()
    with open(path_changed, "r", encoding="utf-8") as f:
        text_changed = f.read()
    with open(path_template, "r", encoding="utf-8") as f:
        text_template = f.read()

    r1 = compare_texts_with_template(
        text_original,
        text_changed,
        text_template,
        k=5,
        name_a=os.path.basename(path_original),
        name_b=os.path.basename(path_changed),
    )


    store_compare_result_as_html(
        base_dir = r1["base_dir"],
        name_a = r1["name_a"],
        name_b = r1["name_b"],
        text_a = r1["text_a"],
        text_b = r1["text_b"],
        similarity = r1["similarity"],
        overlap = r1["overlap"],
        groups = r1["groups"],
    )

    r1 = compare_files(path_original, path_changed)


    store_compare_result_as_html(
        base_dir = r1["base_dir"],
        name_a = r1["name_a"],
        name_b = r1["name_b"],
        text_a = r1["text_a"],
        text_b = r1["text_b"],
        similarity = r1["similarity"],
        overlap = r1["overlap"],
        groups = r1["groups"],
    )
    # print()
    # r2 = compare_files(path_original, path_change_var_names)
    # store_compare_result_as_html(**r2)


if __name__ == "__main__":
    main()
