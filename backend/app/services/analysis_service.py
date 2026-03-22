"""Analysis service: baseline similarity run.

Loads merged submission files for an assignment, computes pairwise similarity,
and stores results in the similarity_results collection (one doc per run).
"""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from pymongo.database import Database

from app.analysis.testWinowingCode.testWinowingLib import compute_similarity_from_text


def run_analysis_for_assignment(
    db: Database, assignment_id: str, run_id: str
) -> None:
    """Run the similarity-analysis pipeline for one assignment.

    Writes one document to the similarity_results collection:
    {runId, assignmentId, createdAt, pairs:[{submissionA, submissionB, score}]}
    """
    submissions = list(
        db["submissions"].find(
            {"assignmentId": assignment_id, "status": "processed"},
            {"_id": 1, "mergedStoragePath": 1},
        )
    )

    print("run analysis for assignment", assignment_id, flush=True)

    # Deterministic ordering
    submissions.sort(key=lambda s: str(s.get("_id", "")))

    prepared: list[dict[str, str]] = []
    for s in submissions:
        merged_path = s.get("mergedStoragePath")
        submission_id = str(s.get("_id"))

        text = ""
        if merged_path:
            try:
                text = Path(merged_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""

        prepared.append({"submissionId": submission_id, "text": text})

    pairs: list[dict[str, object]] = []
    for a, b in combinations(prepared, 2):
        score = compute_similarity_from_text(a["text"], b["text"], k=5)
        pairs.append(
            {
                "submissionA": a["submissionId"],
                "submissionB": b["submissionId"],
                "score": score,
            }
        )

    result_doc = {
        "runId": run_id,
        "assignmentId": assignment_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "pairs": pairs,
    }

    # One result document per run.
    db["similarity_results"].update_one(
        {"runId": run_id},
        {"$set": result_doc},
        upsert=True,
    )
