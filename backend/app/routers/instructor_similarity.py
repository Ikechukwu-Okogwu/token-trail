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
from app.services.analysis_service import (
    build_similarity_metrics,
    load_submission_text_and_path,
    resolve_pair_result_id,
)
from app.services.anonymization_service import pseudonymize_student_identifier

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


def _get_authorized_run_and_assignment(db, run_id: str, instructor_id: str) -> tuple[dict, dict]:
    run = db.analysis_runs.find_one({"_id": to_object_id(run_id)})
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    assignment = db.assignments.find_one({"_id": to_object_id(run["assignmentId"])})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": instructor_id}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your analysis run")
    return run, assignment


def _find_pair_by_result_id(db, result_id: str) -> tuple[str, dict, int]:
    """Find a pair by its stored resultId, with fallback to index format."""
    # Validate: must contain "__" (new format) or end with "-<digits>" (old fallback)
    has_double_underscore = "__" in result_id
    maybe_run_id, sep, maybe_idx = result_id.rpartition("-")
    has_index_format = sep and maybe_idx.isdigit()
    if not has_double_underscore and not has_index_format:
        raise HTTPException(
            status_code=400,
            detail="Invalid resultId format. Expected runId__leftSubmissionId__rightSubmissionId",
        )

    doc = db.similarity_results.find_one({"pairs.resultId": result_id}, {"runId": 1, "pairs": 1})
    if doc:
        for idx, pair in enumerate(doc.get("pairs", []), start=1):
            if pair.get("resultId") == result_id:
                return doc["runId"], pair, idx

    # Fallback: parse "<runId>-<pairIndex>" format
    if has_index_format:
        fallback_doc = db.similarity_results.find_one(
            {"runId": maybe_run_id},
            {"runId": 1, "pairs": 1},
        )
        if fallback_doc:
            pair_index = int(maybe_idx)
            pairs = fallback_doc.get("pairs", [])
            if 1 <= pair_index <= len(pairs):
                return fallback_doc["runId"], pairs[pair_index - 1], pair_index

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

    submission_ids = {
        str(pair.get("submissionA", ""))
        for pair in ranked_pairs
        if str(pair.get("submissionA", ""))
    } | {
        str(pair.get("submissionB", ""))
        for pair in ranked_pairs
        if str(pair.get("submissionB", ""))
    }
    submission_map = {}
    if submission_ids:
        submission_docs = db.submissions.find(
            {"_id": {"$in": [to_object_id(sid) for sid in submission_ids]}}
        )
        submission_map = {str(doc["_id"]): doc for doc in submission_docs}

    items = [
        SimilarityResultListItem(
            resultId=resolve_pair_result_id(str(run["_id"]), pair, idx),
            runId=str(run["_id"]),
            assignmentId=str(assignment["_id"]),
            leftSubmissionId=str(pair.get("submissionA", "")),
            leftStudentIdentifier=pseudonymize_student_identifier(
                str(
                    submission_map.get(str(pair.get("submissionA", "")), {}).get(
                        "studentIdentifier", ""
                    )
                )
            ),
            leftStudentName=pseudonymize_student_identifier(
                submission_map.get(str(pair.get("submissionA", "")), {}).get("studentName")
            ) if submission_map.get(str(pair.get("submissionA", "")), {}).get("studentName") else None,
            rightSubmissionId=str(pair.get("submissionB", "")),
            rightStudentIdentifier=pseudonymize_student_identifier(
                str(
                    submission_map.get(str(pair.get("submissionB", "")), {}).get(
                        "studentIdentifier", ""
                    )
                )
            ),
            rightStudentName=pseudonymize_student_identifier(
                submission_map.get(str(pair.get("submissionB", "")), {}).get("studentName")
            ) if submission_map.get(str(pair.get("submissionB", "")), {}).get("studentName") else None,
            similarityScore=float(pair.get("score", 0.0)),
            confidence=float(pair.get("confidence", 0.0)),
            largestBlockSize=int(pair.get("largestBlockSize", 0)),
            analysisMethod=pair.get("analysisMethod") or "tokenize",
            warnings=pair.get("warnings") or [],
        )
        for idx, pair in enumerate(ranked_pairs, start=1)
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
    db = get_db()
    run_id, pair, _ = _find_pair_by_result_id(db, result_id)
    run, assignment = _get_authorized_run_and_assignment(db, run_id, current["id"])

    left_submission = db.submissions.find_one({"_id": to_object_id(str(pair["submissionA"]))})
    right_submission = db.submissions.find_one({"_id": to_object_id(str(pair["submissionB"]))})
    if not left_submission or not right_submission:
        raise HTTPException(status_code=404, detail="Submission not found for similarity pair")

    if (
        left_submission.get("assignmentId") != str(assignment["_id"])
        or right_submission.get("assignmentId") != str(assignment["_id"])
    ):
        raise HTTPException(status_code=404, detail="Submission assignment mismatch")

    return SimilarityPairDetailResponse(
        resultId=result_id,
        runId=str(run["_id"]),
        assignmentId=str(assignment["_id"]),
        leftSubmissionId=str(pair.get("submissionA")),
        leftStudentIdentifier=pseudonymize_student_identifier(str(left_submission.get("studentIdentifier") or "")),
        leftStudentName=pseudonymize_student_identifier(left_submission.get("studentName")) if left_submission.get("studentName") else None,
        rightSubmissionId=str(pair.get("submissionB")),
        rightStudentIdentifier=pseudonymize_student_identifier(str(right_submission.get("studentIdentifier") or "")),
        rightStudentName=pseudonymize_student_identifier(right_submission.get("studentName")) if right_submission.get("studentName") else None,
        similarityScore=float(pair.get("score", 0.0)),
        summary=pair.get("summary") or "Pair similarity computed from merged submission sources.",
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
    db = get_db()
    run_id, pair, pair_index = _find_pair_by_result_id(db, result_id)
    run, assignment = _get_authorized_run_and_assignment(db, run_id, current["id"])

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

    # Use stored regions if analysis_service already computed them; otherwise compute now
    persisted_regions = pair.get("matchingRegions")
    persisted_excluded = pair.get("excludedRegions")

    if persisted_regions is not None and persisted_excluded is not None:
        metrics = {
            "matchingRegions": persisted_regions,
            "excludedRegions": persisted_excluded,
            "summary": pair.get("summary") or f"Detected {len(persisted_regions)} matched block(s).",
            "confidence": float(pair.get("confidence", 0.0)),
            "snippets": pair.get("snippets") or [
                r.get("snippet", "") for r in persisted_regions if r.get("snippet")
            ],
        }
    else:
        lang = (assignment.get("language") or "").strip().lower()
        metrics = build_similarity_metrics(left_code, right_code, k=5, language=lang)

    # Propagate pair-level warnings and analysisMethod from stored data
    pair_warnings = pair.get("warnings") or []
    analysis_method = pair.get("analysisMethod") or "tokenize"

    return SimilarityComparisonResponse(
        resultId=result_id,
        runId=str(run["_id"]),
        assignmentId=str(assignment["_id"]),
        leftSubmissionId=str(pair.get("submissionA")),
        leftStudentIdentifier=pseudonymize_student_identifier(str(left_submission.get("studentIdentifier") or "")),
        leftStudentName=pseudonymize_student_identifier(left_submission.get("studentName")) if left_submission.get("studentName") else None,
        rightSubmissionId=str(pair.get("submissionB")),
        rightStudentIdentifier=pseudonymize_student_identifier(str(right_submission.get("studentIdentifier") or "")),
        rightStudentName=pseudonymize_student_identifier(right_submission.get("studentName")) if right_submission.get("studentName") else None,
        similarityScore=float(pair.get("score", 0.0)),
        leftFilePath=left_path,
        rightFilePath=right_path,
        leftCode=left_code,
        rightCode=right_code,
        matchingRegions=metrics["matchingRegions"],
        excludedRegions=metrics["excludedRegions"],
        summary=str(metrics["summary"]),
        confidence=float(metrics["confidence"]),
        snippets=[s for s in metrics["snippets"] if s],
        analysisMethod=analysis_method,
        warnings=pair_warnings,
    )
