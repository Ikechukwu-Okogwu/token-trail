# -*- coding: utf-8 -*-
"""
Test winnowing library: compare two files from similarCodes folder.
Run with project venv: venv\\Scripts\\python.exe testWinowingLib.py
"""

import os
from collections import defaultdict

# Support both:
# - importing as a package module (used by the backend)
# - running this file directly as a script (original dev workflow)
try:
    from .winnowingCopy import winnow
except ImportError:  # pragma: no cover
    from winnowingCopy import winnow


def load_file(path):
    """Load file content as string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fingerprint_hashes(fingerprints):
    """Extract hash values from fingerprints (set of (position, hash) tuples)."""
    return {h for _, h in fingerprints}

def fingerprint_index(fingerprints):
    """Build hash -> [positions] index from (position, hash) fingerprints."""
    index = defaultdict(list)
    for pos, hs in fingerprints:
        index[hs].append(pos)
    for hs in index:
        index[hs].sort()
    return index


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
    groups,
):
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
        a_start = min(x[0] for x in g)
        a_end = max(x[0] for x in g)
        b_start = min(x[1] for x in g)
        b_end = max(x[1] for x in g)
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


def build_match_points(index_a, index_b, common_hashes, max_pos_each=10):
    """
    Build match points between two files from common hashes.

    Returns a list of tuples: (pos_a, pos_b, hs, delta) where delta = pos_b - pos_a.
    To avoid combinatorial explosion, we only use up to max_pos_each positions per hash
    on each side.
    """
    points = []
    for hs in common_hashes:
        # Debug: show hashes that are truncated (occur too many times)
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
                points.append((pa, pb, hs, pb - pa))
    return points


def group_match_points(points, min_group_size=4, delta_tol=5, max_gap=120):
    """
    Group match points into "continuous" diagonal-like segments.

    Heuristic: points in the same group should
    - have similar delta (pos_b - pos_a)
    - be increasing in both pos_a and pos_b
    - not jump too far between consecutive points
    """
    if not points:
        return []

    pts = sorted(points, key=lambda t: (t[3], t[0], t[1]))
    groups = []
    cur = []

    for p in pts:
        if not cur:
            cur = [p]
            continue

        prev = cur[-1]
        same_diag = abs(p[3] - prev[3]) <= delta_tol
        increasing = p[0] >= prev[0] and p[1] >= prev[1]
        close_enough = (p[0] - prev[0]) <= max_gap and (p[1] - prev[1]) <= max_gap

        if same_diag and increasing and close_enough:
            cur.append(p)
        else:
            if len(cur) >= min_group_size:
                groups.append(cur)
            cur = [p]

    if len(cur) >= min_group_size:
        groups.append(cur)

    # Largest groups first, then by earliest occurrence
    groups.sort(key=lambda g: (-len(g), min(x[0] for x in g)))
    return groups


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
    if not text_a or not text_b:
        return 0.0
    if not text_a.strip() or not text_b.strip():
        return 0.0

    fp_a = winnow(text_a, k=k)
    fp_b = winnow(text_b, k=k)

    hashes_a = fingerprint_hashes(fp_a)
    hashes_b = fingerprint_hashes(fp_b)

    return float(jaccard_similarity(hashes_a, hashes_b))


def compare_files(path_a, path_b):
    """Compare two files with winnowing and print similarity."""
    name_a = os.path.basename(path_a)
    name_b = os.path.basename(path_b)

    text_a = load_file(path_a)
    text_b = load_file(path_b)

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
    store_compare_result(
        base_dir=os.path.dirname(os.path.abspath(__file__)),
        name_a=name_a,
        name_b=name_b,
        text_a=text_a,
        text_b=text_b,
        similarity=similarity,
        overlap=overlap,
        groups=groups,
    )

    print("-" * 50)


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    # Reset outputs each run
    open(os.path.join(base, "original.txt"), "w", encoding="utf-8").close()
    open(os.path.join(base, "compared.txt"), "w", encoding="utf-8").close()
    similar_codes_dir = os.path.join(base, "similarCodes")
    path_original = os.path.join(similar_codes_dir, "original.py")
    path_copied = os.path.join(similar_codes_dir, "copied.py")
    path_change_var_names = os.path.join(similar_codes_dir, "changeVarNames.py")

    compare_files(path_original, path_copied)
    print()
    compare_files(path_original, path_change_var_names)


if __name__ == "__main__":
    main()
