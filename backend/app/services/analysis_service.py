"""Analysis service: similarity run with language-dispatched engine.

Language dispatch:
  - Java  → AST/token pipeline (run_tokenize_similarity_pipeline), rename-robust,
             template-aware via AST class-level byte-span exclusion.
  - C/C++ → character k-gram winnowing (compare_texts_with_template), unchanged.
  - Java fallback (parse failure / empty tokens) → character winnowing.

The public API surface (build_similarity_metrics output contract, run_analysis_for_assignment)
is unchanged. Routers, schemas, and frontend require no modification.

Architectural note: _character_winnowing_metrics is kept as a named helper so that
a future C/C++ AST engine can replace the C/C++ dispatch branch without touching
the Java path or the service contract.
"""
from __future__ import annotations

from bisect import bisect_right
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from app.analysis.testWinowingCode.testWinowingLib import compare_texts_with_template

try:
    from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
        TokenizePipelineResult,
        run_tokenize_similarity_pipeline,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.json_kgram_strategy import (
        JsonLeafKgramStrategy,
    )
    from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
        group_token_span_bounds,
    )
    _JAVA_TOKENIZE_AVAILABLE = True
except Exception:
    _JAVA_TOKENIZE_AVAILABLE = False


# ---------------------------------------------------------------------------
# Private helpers (shared by both engine paths)
# ---------------------------------------------------------------------------

def _read_text(path_str: str | None) -> str:
    """Read text from a merged submission file path."""
    if not path_str:
        return ""
    try:
        return Path(path_str).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for idx, ch in enumerate(text):
        if ch == "\n" and idx + 1 < len(text):
            starts.append(idx + 1)
    return starts


def _offset_to_line(text: str, starts: list[int], offset: int) -> int:
    if not text:
        return 1
    safe = min(max(offset, 0), len(text) - 1)
    return bisect_right(starts, safe)


def _line_count(text: str) -> int:
    return len(text.splitlines()) if text else 0


def _extract_snippet(text: str, start_line: int, max_lines: int = 3) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    begin = max(start_line - 1, 0)
    end = min(begin + max_lines, len(lines))
    return "\n".join(lines[begin:end]).strip()


def _merge_line_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not ranges:
        return []
    ordered = sorted(ranges, key=lambda r: (r[0], r[1]))
    merged: list[list[int]] = [[ordered[0][0], ordered[0][1]]]
    for start, end in ordered[1:]:
        current = merged[-1]
        if start <= current[1] + 1:
            current[1] = max(current[1], end)
        else:
            merged.append([start, end])
    return [(s, e) for s, e in merged]


def _build_excluded_for_side(
    *,
    total_lines: int,
    matched_ranges: list[tuple[int, int]],
    side: str,
) -> list[dict[str, object]]:
    if total_lines <= 0:
        return []
    merged = _merge_line_ranges(matched_ranges)
    cursor = 1
    out: list[dict[str, object]] = []
    for start, end in merged:
        if cursor < start:
            out.append(
                {
                    "leftStartLine": cursor if side == "left" else None,
                    "leftEndLine": start - 1 if side == "left" else None,
                    "rightStartLine": cursor if side == "right" else None,
                    "rightEndLine": start - 1 if side == "right" else None,
                    "evidenceType": "non_match",
                    "reason": "No matching fingerprint group",
                }
            )
        cursor = end + 1
    if cursor <= total_lines:
        out.append(
            {
                "leftStartLine": cursor if side == "left" else None,
                "leftEndLine": total_lines if side == "left" else None,
                "rightStartLine": cursor if side == "right" else None,
                "rightEndLine": total_lines if side == "right" else None,
                "evidenceType": "non_match",
                "reason": "No matching fingerprint group",
            }
        )
    return out


def _confidence_and_coverage(
    similarity: float,
    left_ranges: list[tuple[int, int]],
    right_ranges: list[tuple[int, int]],
    text_a: str,
    text_b: str,
) -> float:
    """Shared confidence formula: 0.55 * similarity + 0.45 * mean_line_coverage."""
    left_total = _line_count(text_a)
    right_total = _line_count(text_b)
    left_matched = sum(e - s + 1 for s, e in _merge_line_ranges(left_ranges))
    right_matched = sum(e - s + 1 for s, e in _merge_line_ranges(right_ranges))
    left_cov = left_matched / left_total if left_total else 0.0
    right_cov = right_matched / right_total if right_total else 0.0
    coverage = (left_cov + right_cov) / 2
    return round(min(1.0, (0.55 * similarity) + (0.45 * coverage)), 4)


# ---------------------------------------------------------------------------
# Java AST/token adapter
# ---------------------------------------------------------------------------

def _tokenize_result_to_metrics(
    result: "TokenizePipelineResult",
    text_a: str,
    text_b: str,
) -> dict[str, object]:
    """Convert a TokenizePipelineResult into the canonical service metrics dict.

    All 7 required fields are preserved:
      similarity, matchingRegions, excludedRegions, confidence,
      snippets, largestBlockSize, summary.

    Region score is the fraction of total fingerprint pairs belonging to each
    group (mirrors the character-path's len(group) / total_points).
    evidenceType is set to "tokenize_group" to distinguish from the
    character-winnowing path ("winnowing_group") in the stored JSON.
    """
    tokens_a = result.tokens_a
    tokens_b = result.tokens_b
    k = result.strategy_k
    na, nb = len(tokens_a), len(tokens_b)
    total_pairs = sum(len(g.pairs) for g in result.groups) or 1

    matching_regions: list[dict[str, object]] = []
    left_ranges: list[tuple[int, int]] = []
    right_ranges: list[tuple[int, int]] = []
    largest_block_size = 0

    for g in result.groups:
        lo_a, hi_a = group_token_span_bounds(g, side="a", k=k, n_tokens=na)
        lo_b, hi_b = group_token_span_bounds(g, side="b", k=k, n_tokens=nb)
        if hi_a < lo_a or hi_b < lo_b:
            continue

        ls_a = min(tokens_a[i].start_line for i in range(lo_a, hi_a + 1))
        le_a = max(tokens_a[i].end_line for i in range(lo_a, hi_a + 1))
        ls_b = min(tokens_b[i].start_line for i in range(lo_b, hi_b + 1))
        le_b = max(tokens_b[i].end_line for i in range(lo_b, hi_b + 1))

        left_block = max(0, le_a - ls_a + 1)
        right_block = max(0, le_b - ls_b + 1)
        largest_block_size = max(largest_block_size, left_block, right_block)

        left_ranges.append((ls_a, le_a))
        right_ranges.append((ls_b, le_b))

        region_score = round(len(g.pairs) / total_pairs, 4)
        matching_regions.append(
            {
                "leftStartLine": ls_a,
                "leftEndLine": le_a,
                "rightStartLine": ls_b,
                "rightEndLine": le_b,
                "score": region_score,
                "evidenceType": "tokenize_group",
                "snippet": _extract_snippet(text_a, ls_a, max_lines=3),
            }
        )

    similarity = float(result.similarity)
    confidence = _confidence_and_coverage(similarity, left_ranges, right_ranges, text_a, text_b)

    left_total = _line_count(text_a)
    right_total = _line_count(text_b)
    excluded_regions = _build_excluded_for_side(
        total_lines=left_total,
        matched_ranges=left_ranges,
        side="left",
    ) + _build_excluded_for_side(
        total_lines=right_total,
        matched_ranges=right_ranges,
        side="right",
    )

    snippets = [r["snippet"] for r in matching_regions if r["snippet"]]
    summary = (
        f"Detected {len(matching_regions)} matched block(s) "
        f"with similarity score {similarity:.2%}."
    )

    return {
        "similarity": round(similarity, 4),
        "matchingRegions": matching_regions,
        "excludedRegions": excluded_regions,
        "summary": summary,
        "confidence": confidence,
        "snippets": snippets,
        "largestBlockSize": largest_block_size,
    }


# ---------------------------------------------------------------------------
# Character-winnowing path (C, C++, Java fallback)
# ---------------------------------------------------------------------------

def _character_winnowing_metrics(
    text_a: str,
    text_b: str,
    *,
    template_text: str = "",
    k: int = 5,
) -> dict[str, object]:
    """Character k-gram winnowing path used for C, C++, and Java parse fallback.

    Kept as a named function so a future C/C++ AST engine can replace the
    C/C++ dispatch branch without touching Java logic or the service contract.
    """
    result = compare_texts_with_template(text_a, text_b, template_text, k=k)
    groups = result.get("groups", [])
    similarity = float(result.get("similarity", 0.0))

    starts_a = _line_starts(text_a)
    starts_b = _line_starts(text_b)
    total_points = sum(len(g) for g in groups) or 1

    matching_regions: list[dict[str, object]] = []
    left_ranges: list[tuple[int, int]] = []
    right_ranges: list[tuple[int, int]] = []
    largest_block_size = 0

    for group in groups:
        left_start_char = min(p.pos_a for p in group)
        left_end_char = max(p.pos_a for p in group)
        right_start_char = min(p.pos_b for p in group)
        right_end_char = max(p.pos_b for p in group)

        left_start_line = _offset_to_line(text_a, starts_a, left_start_char)
        left_end_line = _offset_to_line(text_a, starts_a, left_end_char)
        right_start_line = _offset_to_line(text_b, starts_b, right_start_char)
        right_end_line = _offset_to_line(text_b, starts_b, right_end_char)

        left_block_size = max(0, left_end_line - left_start_line + 1)
        right_block_size = max(0, right_end_line - right_start_line + 1)
        largest_block_size = max(largest_block_size, left_block_size, right_block_size)

        left_ranges.append((left_start_line, left_end_line))
        right_ranges.append((right_start_line, right_end_line))

        matching_regions.append(
            {
                "leftStartLine": left_start_line,
                "leftEndLine": left_end_line,
                "rightStartLine": right_start_line,
                "rightEndLine": right_end_line,
                "score": round(len(group) / total_points, 4),
                "evidenceType": "winnowing_group",
                "snippet": _extract_snippet(text_a, left_start_line, max_lines=3),
            }
        )

    left_total_lines = _line_count(text_a)
    right_total_lines = _line_count(text_b)
    confidence = _confidence_and_coverage(
        similarity, left_ranges, right_ranges, text_a, text_b
    )

    excluded_regions = _build_excluded_for_side(
        total_lines=left_total_lines,
        matched_ranges=left_ranges,
        side="left",
    ) + _build_excluded_for_side(
        total_lines=right_total_lines,
        matched_ranges=right_ranges,
        side="right",
    )

    summary = (
        f"Detected {len(matching_regions)} matched block(s) "
        f"with similarity score {similarity:.2%}."
    )
    snippets = [region["snippet"] for region in matching_regions if region["snippet"]]

    return {
        "similarity": round(similarity, 4),
        "matchingRegions": matching_regions,
        "excludedRegions": excluded_regions,
        "summary": summary,
        "confidence": confidence,
        "snippets": snippets,
        "largestBlockSize": largest_block_size,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_similarity_metrics(
    text_a: str,
    text_b: str,
    *,
    template_text: str = "",
    k: int = 5,
    language: str = "",
) -> dict[str, object]:
    """Compute score + block-level data used by ranked and comparison endpoints.

    Dispatch:
      - Java  → AST/token pipeline (rename-robust, AST template exclusion).
                Falls back to character winnowing on parse failure or empty tokens.
      - C/C++ → character winnowing (behaviour unchanged from before Phase B).
    """
    if language == "java" and _JAVA_TOKENIZE_AVAILABLE and text_a.strip() and text_b.strip():
        try:
            result = run_tokenize_similarity_pipeline(
                text_a,
                text_b,
                template=template_text,
                strategy=JsonLeafKgramStrategy(k=k),
            )
            return _tokenize_result_to_metrics(result, text_a, text_b)
        except Exception:
            pass  # fall through to character-winnowing path

    # C, C++, and Java fallback
    return _character_winnowing_metrics(text_a, text_b, template_text=template_text, k=k)


def resolve_pair_result_id(run_id: str, pair: dict, pair_index: int) -> str:
    """Resolve a stable resultId for a pair, creating fallback if missing."""
    value = pair.get("resultId")
    if isinstance(value, str) and value:
        return value
    return f"{run_id}-{pair_index}"


def load_submission_text_and_path(db: Database, submission_id: str) -> tuple[str, str]:
    """Read merged text and file path for a submission id."""
    try:
        oid = ObjectId(submission_id)
    except (InvalidId, TypeError):
        return "", ""
    doc = db["submissions"].find_one({"_id": oid}, {"mergedStoragePath": 1})
    if not doc:
        return "", ""
    path = doc.get("mergedStoragePath") or ""
    return path, _read_text(path)


def run_analysis_for_assignment(
    db: Database, assignment_id: str, run_id: str
) -> None:
    """Run the similarity-analysis pipeline for one assignment."""
    # Fetch assignment to get optional template exclusion code and language
    assignment = db["assignments"].find_one(
        {"_id": ObjectId(assignment_id)},
        {"exclusionCode": 1, "language": 1},
    )
    template_text: str = (assignment or {}).get("exclusionCode") or ""
    language: str = ((assignment or {}).get("language") or "").lower()

    submissions = list(
        db["submissions"].find(
            {"assignmentId": assignment_id, "status": "processed"},
            {"_id": 1, "mergedStoragePath": 1},
        )
    )

    submissions.sort(key=lambda s: str(s.get("_id", "")))

    prepared: list[dict[str, str]] = []
    for s in submissions:
        merged_path = s.get("mergedStoragePath")
        submission_id = str(s.get("_id"))
        prepared.append(
            {
                "submissionId": submission_id,
                "path": merged_path or "",
                "text": _read_text(merged_path),
            }
        )

    pairs: list[dict[str, object]] = []
    for pair_index, (a, b) in enumerate(combinations(prepared, 2), start=1):
        metrics = build_similarity_metrics(
            a["text"], b["text"],
            template_text=template_text,
            k=5,
            language=language,
        )
        pairs.append(
            {
                "resultId": f"{run_id}__{a['submissionId']}__{b['submissionId']}",
                "submissionA": a["submissionId"],
                "submissionB": b["submissionId"],
                "score": metrics["similarity"],
                "confidence": metrics["confidence"],
                "largestBlockSize": metrics["largestBlockSize"],
                "summary": metrics["summary"],
                "matchingRegions": metrics["matchingRegions"],
                "excludedRegions": metrics["excludedRegions"],
                "snippets": metrics["snippets"],
            }
        )

    result_doc = {
        "runId": run_id,
        "assignmentId": assignment_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "pairs": pairs,
    }

    db["similarity_results"].update_one(
        {"runId": run_id},
        {"$set": result_doc},
        upsert=True,
    )
