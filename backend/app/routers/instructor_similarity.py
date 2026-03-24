"""Instructor similarity-report routes (JWT required)."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.db import get_db
from app.core.deps import get_current_instructor
from app.schemas.common import NotImplementedResponse
from app.schemas.similarity import (
    SimilarityComparisonResponse,
    SimilarityResultListItem,
    SimilarityResultsResponse,
)
from app.services.analysis_service import (
    build_similarity_metrics,
    load_submission_text_and_path,
    resolve_pair_result_id,
)

router = APIRouter(prefix="/instructor", tags=["instructor-similarity"])


def _not_implemented(feature: str) -> JSONResponse:
    """Return a standard skeleton placeholder response."""
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "feature": feature,
            "message": "Skeleton placeholder endpoint. Implementation planned in future sprint.",
        },
    )


def _get_authorized_run_and_assignment(db, run_id: str, instructor_id: str) -> tuple[dict, dict]:
    from app.core.deps import to_object_id
    from bson import ObjectId

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
    doc = db.similarity_results.find_one({"pairs.resultId": result_id}, {"runId": 1, "pairs": 1})
    if doc:
        for idx, pair in enumerate(doc.get("pairs", []), start=1):
            if pair.get("resultId") == result_id:
                return doc["runId"], pair, idx

    # Backward compatibility fallback: parse result id in the shape "<runId>-<pairIndex>"
    maybe_run_id, sep, maybe_idx = result_id.rpartition("-")
    if sep and maybe_idx.isdigit():
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
    """Return ranked similarity rows for one analysis run."""
    db = get_db()
    run, _assignment = _get_authorized_run_and_assignment(db, run_id, current["id"])
    result_doc = db.similarity_results.find_one({"runId": run_id}, {"pairs": 1})
    pairs = result_doc.get("pairs", []) if result_doc else []

    sorted_pairs = sorted(
        pairs,
        key=lambda pair: float(pair.get("score", 0.0)),
        reverse=True,
    )
    results: list[SimilarityResultListItem] = []
    for idx, pair in enumerate(sorted_pairs, start=1):
        results.append(
            SimilarityResultListItem(
                resultId=resolve_pair_result_id(run_id, pair, idx),
                assignmentId=run["assignmentId"],
                leftSubmissionId=str(pair.get("submissionA", "")),
                rightSubmissionId=str(pair.get("submissionB", "")),
                similarityScore=float(pair.get("score", 0.0)),
                confidence=float(pair.get("confidence", 0.0)),
                largestBlockSize=int(pair.get("largestBlockSize", 0)),
            )
        )

    return SimilarityResultsResponse(runId=run_id, results=results)


@router.get("/similarity-results/{result_id}", response_model=NotImplementedResponse)
async def get_similarity_pair_detail(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: pair drill-down details."""
    _ = (result_id, current)
    return _not_implemented("similarity_pair_detail")


@router.get(
    "/similarity-results/{result_id}/comparison",
    response_model=SimilarityComparisonResponse,
)
async def get_similarity_side_by_side_comparison(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Return side-by-side highlighted comparison payload."""
    db = get_db()
    run_id, pair, pair_index = _find_pair_by_result_id(db, result_id)
    _run, _assignment = _get_authorized_run_and_assignment(db, run_id, current["id"])

    left_submission_id = str(pair.get("submissionA", ""))
    right_submission_id = str(pair.get("submissionB", ""))
    left_file_path, left_text = load_submission_text_and_path(db, left_submission_id)
    right_file_path, right_text = load_submission_text_and_path(db, right_submission_id)

    persisted_regions = pair.get("matchingRegions")
    persisted_excluded = pair.get("excludedRegions")
    persisted_summary = pair.get("summary")
    persisted_confidence = pair.get("confidence")
    persisted_snippets = pair.get("snippets")

    if persisted_regions is None or persisted_excluded is None:
        computed = build_similarity_metrics(left_text, right_text, k=5)
    else:
        computed = {
            "matchingRegions": persisted_regions,
            "excludedRegions": persisted_excluded,
            "summary": persisted_summary
            or f"Detected {len(persisted_regions)} matched block(s).",
            "confidence": float(persisted_confidence or 0.0),
            "snippets": persisted_snippets
            or [region.get("snippet", "") for region in persisted_regions if region.get("snippet")],
        }

    return SimilarityComparisonResponse(
        resultId=resolve_pair_result_id(run_id, pair, pair_index),
        leftFilePath=left_file_path,
        rightFilePath=right_file_path,
        matchingRegions=computed["matchingRegions"],
        excludedRegions=computed["excludedRegions"],
        summary=str(computed["summary"]),
        confidence=float(computed["confidence"]),
        snippets=[snippet for snippet in computed["snippets"] if snippet],
    )
