"""Instructor admin routes (JWT required)."""
from datetime import datetime, timezone
from pathlib import Path
import shutil

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse

from app.core.config import UPLOAD_DIR
from app.core.db import get_db
from app.core.deps import get_current_instructor, to_object_id
from app.routers.instructor import _assignment_response, _generate_assignment_key
from app.schemas.assignment import AssignmentResponse
from app.schemas.exclusion import ExclusionCodeResponse, ExclusionCodeUpsertRequest
from app.services.zip_service import build_submissions_archive

router = APIRouter(prefix="/instructor", tags=["instructor-admin"])


def _require_owned_assignment(*, assignment_id: str, instructor_id: str) -> dict:
    """Load assignment and enforce ownership through parent course."""
    db = get_db()
    assignment = db.assignments.find_one({"_id": to_object_id(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": instructor_id}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your assignment")
    return assignment


@router.post("/assignments/{assignment_id}/regenerate-key", response_model=AssignmentResponse)
async def regenerate_assignment_key(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Regenerate the assignment's public submission key."""
    db = get_db()
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    new_key = _generate_assignment_key(db)
    db.assignments.update_one({"_id": assignment["_id"]}, {"$set": {"assignmentKey": new_key}})
    updated = db.assignments.find_one({"_id": assignment["_id"]})
    return _assignment_response(updated)


@router.post("/assignments/{assignment_id}/expire-key", response_model=AssignmentResponse)
async def expire_assignment_key(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Expire the assignment key immediately."""
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    now_iso = datetime.now(timezone.utc).isoformat()
    db = get_db()
    db.assignments.update_one({"_id": assignment["_id"]}, {"$set": {"keyExpiry": now_iso}})
    updated = db.assignments.find_one({"_id": assignment["_id"]})
    return _assignment_response(updated)


@router.get("/assignments/{assignment_id}/submissions/download")
async def download_assignment_submissions_zip(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Download all assignment submissions as a ZIP archive."""
    _require_owned_assignment(assignment_id=assignment_id, instructor_id=current["id"])
    db = get_db()
    submissions = list(
        db.submissions.find({"assignmentId": assignment_id}, {"zipStoragePath": 1, "mergedStoragePath": 1})
    )
    payload = build_submissions_archive(assignment_id=assignment_id, submissions=submissions)
    filename = f"assignment-{assignment_id}-submissions.zip"
    return StreamingResponse(
        iter([payload]),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/assignments/{assignment_id}/submissions", status_code=204)
async def delete_assignment_submissions(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Delete all submissions (Mongo + disk) for an assignment."""
    _require_owned_assignment(assignment_id=assignment_id, instructor_id=current["id"])
    db = get_db()
    db.submissions.delete_many({"assignmentId": assignment_id})
    db.analysis_runs.delete_many({"assignmentId": assignment_id})
    db.similarity_results.delete_many({"assignmentId": assignment_id})

    assignment_upload_dir = Path(UPLOAD_DIR) / assignment_id
    if assignment_upload_dir.exists() and assignment_upload_dir.is_dir():
        shutil.rmtree(assignment_upload_dir, ignore_errors=True)
    return Response(status_code=204)


@router.delete("/assignments/{assignment_id}", status_code=204)
async def delete_assignment(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Delete an assignment and cascade cleanup for submissions/results/files."""
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    db = get_db()

    db.submissions.delete_many({"assignmentId": assignment_id})
    db.analysis_runs.delete_many({"assignmentId": assignment_id})
    db.similarity_results.delete_many({"assignmentId": assignment_id})
    db.assignments.delete_one({"_id": assignment["_id"]})

    assignment_upload_dir = Path(UPLOAD_DIR) / assignment_id
    if assignment_upload_dir.exists() and assignment_upload_dir.is_dir():
        shutil.rmtree(assignment_upload_dir, ignore_errors=True)
    return Response(status_code=204)


@router.get("/assignments/{assignment_id}/exclusion-code", response_model=ExclusionCodeResponse)
async def get_exclusion_code(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Read assignment exclusion code."""
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    return ExclusionCodeResponse(
        assignmentId=str(assignment["_id"]),
        exclusionCode=assignment.get("exclusionCode"),
    )


@router.put("/assignments/{assignment_id}/exclusion-code", response_model=ExclusionCodeResponse)
async def upsert_exclusion_code(
    assignment_id: str,
    body: ExclusionCodeUpsertRequest,
    current: dict = Depends(get_current_instructor),
):
    """Add or update assignment exclusion code."""
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    db = get_db()
    db.assignments.update_one(
        {"_id": assignment["_id"]},
        {"$set": {"exclusionCode": body.exclusionCode}},
    )
    updated = db.assignments.find_one({"_id": assignment["_id"]})
    return ExclusionCodeResponse(
        assignmentId=str(updated["_id"]),
        exclusionCode=updated.get("exclusionCode"),
    )


@router.delete("/assignments/{assignment_id}/exclusion-code", response_model=ExclusionCodeResponse)
async def delete_exclusion_code(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Remove assignment exclusion code."""
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    db = get_db()
    db.assignments.update_one({"_id": assignment["_id"]}, {"$set": {"exclusionCode": None}})
    return ExclusionCodeResponse(assignmentId=str(assignment["_id"]), exclusionCode=None)
