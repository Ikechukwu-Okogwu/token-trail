"""Instructor admin routes (JWT required)."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import io
import zipfile

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import MAX_UPLOAD_MB, UPLOAD_DIR
from app.core.db import get_db
from app.core.deps import get_current_instructor, to_object_id
from app.routers.instructor import _assignment_response, _generate_assignment_key
from app.schemas.assignment import AssignmentResponse
from app.schemas.exclusion import ExclusionCodeResponse, ExclusionCodeUpsertRequest
from app.services.merge_service import merge_source_files
from app.services.submission_service import create_submission
from app.services.zip_service import (
    build_submissions_archive,
    list_valid_source_files,
    safe_extract_zip,
)

router = APIRouter(prefix="/instructor", tags=["instructor-admin"])


# ── Import response schema ───────────────────────────

class _ImportedEntry(BaseModel):
    folder: str
    submissionId: str
    fileCount: int

class _SkippedEntry(BaseModel):
    folder: str
    reason: str

class RepositoryImportResponse(BaseModel):
    imported: int
    skipped: int
    details: list[_ImportedEntry]
    skippedDetails: list[_SkippedEntry]


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


@router.post(
    "/assignments/{assignment_id}/submissions/import",
    response_model=RepositoryImportResponse,
    status_code=201,
)
async def import_repository_zip(
    assignment_id: str,
    zipFile: UploadFile = File(...),
    current: dict = Depends(get_current_instructor),
):
    """Import a repository ZIP ("zip of zips") into an assignment.

    Supports two layouts:

    **Format A — flat zip of zips** (spec / round-robin standard)::

        LastYearsCourse.zip
        ├── StudentA.zip        # submission zip with source files
        ├── StudentB.zip
        └── StudentC.zip

    **Format B — folder-per-submission with raw.zip** (Token Trail export)::

        exported.zip
        ├── 6abc…def/
        │   └── raw.zip
        └── 7fed…abc/
            └── raw.zip

    Detection is automatic: if the outer ZIP contains top-level ``.zip``
    entries they are treated as Format A submissions.  Otherwise the
    endpoint falls back to Format B (folder / ``raw.zip``).

    The identifier for each submission is derived from the inner zip
    filename (without ``.zip``) or the folder name respectively.
    """
    assignment = _require_owned_assignment(
        assignment_id=assignment_id,
        instructor_id=current["id"],
    )
    language = assignment["language"]
    db = get_db()

    # ── Read and validate outer ZIP ──────────────────────
    contents = await zipFile.read()
    if len(contents) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"Repository ZIP exceeds {MAX_UPLOAD_MB} MB limit",
        )
    try:
        outer_zf = zipfile.ZipFile(io.BytesIO(contents))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid ZIP")

    # ── Detect format: top-level .zip files vs folder/raw.zip ─
    #
    # Build a list of (identifier, zip_bytes) pairs to process.
    # Format A: top-level entries ending in .zip (no "/" before the name)
    # Format B: <folder>/raw.zip entries
    entries: list[tuple[str, bytes]] = []

    # Check for Format A — top-level .zip files
    for info in outer_zf.infolist():
        name = info.filename
        # Top-level means no "/" in the path (or only a single segment)
        if "/" not in name and name.lower().endswith(".zip"):
            try:
                inner_bytes = outer_zf.read(info)
                identifier = name[:-4]  # strip .zip extension
                entries.append((identifier, inner_bytes))
            except Exception:
                pass

    # If no top-level zips found, fall back to Format B — folder/raw.zip
    if not entries:
        folders: dict[str, list[zipfile.ZipInfo]] = {}
        for info in outer_zf.infolist():
            parts = info.filename.split("/")
            if len(parts) < 2 or not parts[0]:
                continue
            folders.setdefault(parts[0], []).append(info)

        for folder_name, members in sorted(folders.items()):
            raw_member = None
            for m in members:
                if m.filename == f"{folder_name}/raw.zip":
                    raw_member = m
                    break
            if raw_member is None:
                # No raw.zip — but maybe the folder itself contains source
                # files directly (not zipped).  Skip for now.
                continue
            try:
                entries.append((folder_name, outer_zf.read(raw_member)))
            except Exception:
                pass

    outer_zf.close()

    if not entries:
        raise HTTPException(
            status_code=400,
            detail=(
                "Repository ZIP contains no submission zips. "
                "Expected either top-level .zip files (e.g. StudentA.zip, StudentB.zip) "
                "or folders each containing a raw.zip."
            ),
        )

    # ── Collect existing identifiers to detect duplicates ─
    existing_ids = {
        doc["studentIdentifier"]
        for doc in db.submissions.find(
            {"assignmentId": assignment_id},
            {"studentIdentifier": 1},
        )
    }

    imported: list[_ImportedEntry] = []
    skipped: list[_SkippedEntry] = []

    # ── Process each submission entry ────────────────────
    for identifier, inner_zip_bytes in sorted(entries, key=lambda e: e[0]):
        # Check for duplicate
        if identifier in existing_ids:
            skipped.append(_SkippedEntry(
                folder=identifier,
                reason="Duplicate: a submission with this identifier already exists",
            ))
            continue

        # Create submission directory structure
        submission_id = str(ObjectId())
        base = Path(UPLOAD_DIR) / assignment_id / submission_id
        extracted_dir = base / "extracted"
        merged_dir = base / "merged"
        for d in [extracted_dir, merged_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Save the inner zip
        zip_path = base / "raw.zip"
        zip_path.write_bytes(inner_zip_bytes)

        # Validate inner ZIP
        try:
            safe_extract_zip(zip_path, extracted_dir)
        except zipfile.BadZipFile:
            shutil.rmtree(base, ignore_errors=True)
            skipped.append(_SkippedEntry(
                folder=identifier,
                reason="Submission zip is not a valid ZIP file",
            ))
            continue

        # Filter valid source files by language
        source_files = list_valid_source_files(extracted_dir, language)
        if not source_files:
            shutil.rmtree(base, ignore_errors=True)
            skipped.append(_SkippedEntry(
                folder=identifier,
                reason=f"No valid {language} source files found",
            ))
            continue

        # Merge source files
        merged_path = merged_dir / "merged.txt"
        merge_source_files(source_files, extracted_dir, merged_path)

        # Create submission record
        create_submission(
            db,
            submission_id=submission_id,
            assignment_id=assignment_id,
            student_identifier=identifier,
            student_name=identifier,
            student_email=None,
            file_count=len(source_files),
            zip_storage_path=str(zip_path),
            merged_storage_path=str(merged_path),
        )
        existing_ids.add(identifier)

        imported.append(_ImportedEntry(
            folder=identifier,
            submissionId=submission_id,
            fileCount=len(source_files),
        ))

    return RepositoryImportResponse(
        imported=len(imported),
        skipped=len(skipped),
        details=imported,
        skippedDetails=skipped,
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
