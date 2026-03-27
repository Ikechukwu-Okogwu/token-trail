"""Instructor similarity-result routes (JWT required)."""
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_db
from app.core.deps import get_current_instructor, to_object_id
from app.schemas.similarity import (
    SimilarityComparisonResponse,
    SimilarityPairDetailResponse,
    SimilarityResultListItem,
    SimilarityResultsResponse,
)

router = APIRouter(prefix="/instructor", tags=["instructor-similarity"])


def _build_result_id(run_id: str, left_submission_id: str, right_submission_id: str) -> str:
    """Create deterministic result IDs used by detail/comparison routes."""
    return f"{run_id}__{left_submission_id}__{right_submission_id}"


def _parse_result_id(result_id: str) -> tuple[str, str, str]:
    """Parse result IDs in the format runId__leftSubmissionId__rightSubmissionId."""
    parts = result_id.split("__")
    if len(parts) != 3 or not all(parts):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid resultId format. "
                "Expected runId__leftSubmissionId__rightSubmissionId"
            ),
        )
    return parts[0], parts[1], parts[2]


def _load_run_and_verify_owner(db, run_id: str, current: dict) -> tuple[dict, dict]:
    """Load run + assignment and verify instructor ownership."""
    run = db.analysis_runs.find_one({"_id": to_object_id(run_id)})
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    assignment = db.assignments.find_one({"_id": to_object_id(run["assignmentId"])})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your analysis run")

    return run, assignment


def _get_pair_from_result_doc(result_doc: dict, left_id: str, right_id: str) -> dict:
    """Find one pair in a run result document regardless of side ordering."""
    pairs = result_doc.get("pairs", [])
    for pair in pairs:
        submission_a = str(pair.get("submissionA"))
        submission_b = str(pair.get("submissionB"))
        if {submission_a, submission_b} == {left_id, right_id}:
            return pair
    raise HTTPException(status_code=404, detail="Similarity result not found")


@router.get(
    "/analysis-runs/{run_id}/similarity-results",
    response_model=SimilarityResultsResponse,
)
async def get_ranked_similarity_results(
    run_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Return ranked similarity pairs for one analysis run."""
    db = get_db()
    run, assignment = _load_run_and_verify_owner(db, run_id, current)
    result_doc = db.similarity_results.find_one({"runId": str(run["_id"])})
    if not result_doc:
        raise HTTPException(status_code=404, detail="Similarity results not found")

    ranked_pairs = sorted(
        result_doc.get("pairs", []),
        key=lambda p: float(p.get("score", 0.0)),
        reverse=True,
    )
    items = [
        SimilarityResultListItem(
            resultId=_build_result_id(
                str(run["_id"]),
                str(pair.get("submissionA", "")),
                str(pair.get("submissionB", "")),
            ),
            runId=str(run["_id"]),
            assignmentId=str(assignment["_id"]),
            leftSubmissionId=str(pair.get("submissionA", "")),
            rightSubmissionId=str(pair.get("submissionB", "")),
            similarityScore=float(pair.get("score", 0.0)),
        )
        for pair in ranked_pairs
    ]
    return SimilarityResultsResponse(
        runId=str(run["_id"]),
        assignmentId=str(assignment["_id"]),
        results=items,
    )


@router.get("/similarity-results/{result_id}", response_model=SimilarityPairDetailResponse)
async def get_similarity_pair_detail(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Return pair-level details for one similarity result."""
    run_id, left_submission_id, right_submission_id = _parse_result_id(result_id)
    db = get_db()
    run, assignment = _load_run_and_verify_owner(db, run_id, current)

    result_doc = db.similarity_results.find_one({"runId": str(run["_id"])})
    if not result_doc:
        raise HTTPException(status_code=404, detail="Similarity results not found")
    pair = _get_pair_from_result_doc(result_doc, left_submission_id, right_submission_id)

    return SimilarityPairDetailResponse(
        resultId=result_id,
        runId=str(run["_id"]),
        assignmentId=str(assignment["_id"]),
        leftSubmissionId=str(pair.get("submissionA")),
        rightSubmissionId=str(pair.get("submissionB")),
        similarityScore=float(pair.get("score", 0.0)),
        summary="Pair similarity computed from merged submission sources.",
    )


@router.get(
    "/similarity-results/{result_id}/comparison",
    response_model=SimilarityComparisonResponse,
)
async def get_similarity_side_by_side_comparison(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Return side-by-side comparison payload for one similarity pair."""
    run_id, left_submission_id, right_submission_id = _parse_result_id(result_id)
    db = get_db()
    run, assignment = _load_run_and_verify_owner(db, run_id, current)

    result_doc = db.similarity_results.find_one({"runId": str(run["_id"])})
    if not result_doc:
        raise HTTPException(status_code=404, detail="Similarity results not found")
    pair = _get_pair_from_result_doc(result_doc, left_submission_id, right_submission_id)

    left_submission = db.submissions.find_one({"_id": to_object_id(str(pair["submissionA"]))})
    right_submission = db.submissions.find_one({"_id": to_object_id(str(pair["submissionB"]))})
    if not left_submission or not right_submission:
        raise HTTPException(status_code=404, detail="Submission not found for similarity pair")

    if (
        left_submission.get("assignmentId") != str(assignment["_id"])
        or right_submission.get("assignmentId") != str(assignment["_id"])
    ):
        raise HTTPException(status_code=404, detail="Submission assignment mismatch")

    left_path = str(left_submission.get("mergedStoragePath") or "")
    right_path = str(right_submission.get("mergedStoragePath") or "")

    try:
        left_code = Path(left_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        left_code = ""
    try:
        right_code = Path(right_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        right_code = ""

    return SimilarityComparisonResponse(
        resultId=result_id,
        runId=str(run["_id"]),
        assignmentId=str(assignment["_id"]),
        leftSubmissionId=str(pair.get("submissionA")),
        rightSubmissionId=str(pair.get("submissionB")),
        similarityScore=float(pair.get("score", 0.0)),
        leftFilePath=left_path,
        rightFilePath=right_path,
        leftCode=left_code,
        rightCode=right_code,
        # Line-level region extraction is not available in the baseline engine yet.
        matchingRegions=[],
    )
