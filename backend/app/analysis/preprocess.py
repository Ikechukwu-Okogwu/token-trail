"""
Preprocessing cache layer (minimal implementation).

Duty:
- Provide preprocessed content access for analysis by assignmentId.
- For each submission in the assignment, reuse cached preprocessed content if present.
- Otherwise read the submission's merged file, preprocess it, and store it in MongoDB.

Mongo collection: preprocessed_files
Document shape (minimum):
- assignmentId: str
- submissionId: str
- content: str

Notes:
- This is intentionally minimal: preprocess() currently performs light normalization only.
- Cache key is (assignmentId, submissionId). If the merged file can change in the future,
  add an invalidation key (e.g., mergedHash + algorithmVersion).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pymongo.database import Database


@dataclass(frozen=True)
class PreprocessedItem:
    assignmentId: str
    submissionId: str
    content: str


def preprocess(text: str) -> str:
    """Minimal preprocessing.

    Today: normalize newlines and strip trailing whitespace.
    """
    if not text:
        return ""
    # Normalize Windows newlines and remove trailing whitespace noise.

    from testWinowingCode.winnowingCopy import winnow

    return winnow(text)
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def get_or_create_preprocessed(
    db: Database,
    *,
    assignment_id: str,
    submission_id: str,
    merged_storage_path: str | None,
) -> PreprocessedItem:
    """Return cached preprocessed content for one submission, creating it if needed."""
    cached = db["preprocessed_files"].find_one(
        {"assignmentId": assignment_id, "submissionId": submission_id}
    )
    if cached and isinstance(cached.get("content"), str):
        return PreprocessedItem(
            assignmentId=assignment_id, submissionId=submission_id, content=cached["content"]
        )

    raw_text = ""
    if merged_storage_path:
        try:
            raw_text = Path(merged_storage_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            raw_text = ""

    content = preprocess(raw_text)

    db["preprocessed_files"].update_one(
        {"assignmentId": assignment_id, "submissionId": submission_id},
        {"$set": {"assignmentId": assignment_id, "submissionId": submission_id, "content": content}},
        upsert=True,
    )

    return PreprocessedItem(assignmentId=assignment_id, submissionId=submission_id, content=content)


def get_preprocessed_for_assignment(db: Database, assignment_id: str) -> list[PreprocessedItem]:
    """Fetch preprocessed content for all processed submissions of an assignment."""
    submissions: Iterable[dict] = db["submissions"].find(
        {"assignmentId": assignment_id, "status": "processed"},
        {"_id": 1, "mergedStoragePath": 1},
    )

    items: list[PreprocessedItem] = []
    for s in submissions:
        submission_id = str(s.get("_id"))
        items.append(
            get_or_create_preprocessed(
                db,
                assignment_id=assignment_id,
                submission_id=submission_id,
                merged_storage_path=s.get("mergedStoragePath"),
            )
        )

    # Deterministic ordering
    items.sort(key=lambda x: x.submissionId)
    return items