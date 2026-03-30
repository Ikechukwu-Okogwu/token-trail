"""Public router: key-gated student routes (no JWT required)."""
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import MAX_UPLOAD_MB, UPLOAD_DIR
from app.core.db import get_db
from app.schemas.public import (
    SubmissionResponse,
    ValidateKeyAssignmentInfo,
    ValidateKeyRequest,
    ValidateKeyResponse,
)
from app.services.merge_service import merge_source_files
from app.services.submission_service import create_submission
from app.services.zip_service import list_valid_source_files, safe_extract_zip

router = APIRouter(prefix="/public", tags=["public"])


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string into a timezone-aware datetime."""
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@router.post("/assignment-key/validate", response_model=ValidateKeyResponse)
async def validate_assignment_key(body: ValidateKeyRequest):
    """Check whether a 10-digit assignment key is valid."""
    db = get_db()
    assignment = db.assignments.find_one({"assignmentKey": body.assignmentKey})

    if not assignment:
        return ValidateKeyResponse(valid=False, assignment=None)

    return ValidateKeyResponse(
        valid=True,
        assignment=ValidateKeyAssignmentInfo(
            id=str(assignment["_id"]),
            language=assignment["language"],
            isOpen=assignment.get("isOpen", True),
            dueDate=assignment.get("dueDate"),
            allowLate=assignment.get("allowLate", False),
        ),
    )


@router.post("/submissions", response_model=SubmissionResponse, status_code=201)
async def submit(
    assignmentKey: str = Form(...),
    studentIdentifier: str = Form(...),
    studentName: str | None = Form(None),
    zipFile: UploadFile = File(...),
):
    """Upload a ZIP submission for an assignment.

    Pipeline: validate key -> save ZIP -> safe-extract -> filter sources
              -> deterministic merge -> store Submission document.
    """
    db = get_db()

    # 1. Validate assignment key and load assignment
    assignment = db.assignments.find_one({"assignmentKey": assignmentKey})
    if not assignment:
        raise HTTPException(status_code=404, detail="Invalid assignment key")
    if not assignment.get("isOpen", False):
        raise HTTPException(status_code=400, detail="Assignment is closed for submissions")
    if not assignment.get("allowLate", False):
        due_date = _parse_iso_datetime(assignment.get("dueDate"))
        if due_date and datetime.now(timezone.utc) > due_date:
            raise HTTPException(status_code=400, detail="Assignment due date has passed")

    assignment_id = str(assignment["_id"])
    language = assignment["language"]

    # 2. Create submission ID early so we can build directory paths
    submission_id = str(ObjectId())

    # 3. Ensure directory structure exists
    base = Path(UPLOAD_DIR) / assignment_id / submission_id
    extracted_dir = base / "extracted"
    merged_dir = base / "merged"
    for d in [extracted_dir, merged_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 4. Read and save the raw ZIP
    contents = await zipFile.read()
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail=f"File exceeds {MAX_UPLOAD_MB} MB limit"
        )
    zip_path = base / "raw.zip"
    zip_path.write_bytes(contents)

    # 5. Safe-extract (blocks ../ and absolute path traversal)
    safe_extract_zip(zip_path, extracted_dir)

    # 6. Filter valid source files by language
    source_files = list_valid_source_files(extracted_dir, language)

    # 7. Merge valid files deterministically (sorted by relative path)
    merged_path = merged_dir / "merged.txt"
    merge_source_files(source_files, extracted_dir, merged_path)

    # 8. Persist Submission document in MongoDB
    doc = create_submission(
        db,
        submission_id=submission_id,
        assignment_id=assignment_id,
        student_identifier=studentIdentifier,
        student_name=studentName,
        file_count=len(source_files),
        zip_storage_path=str(zip_path),
        merged_storage_path=str(merged_path),
    )

    return SubmissionResponse(
        submissionId=submission_id,
        status=doc["status"],
        fileCount=len(source_files),
        mergedCreated=True,
    )
