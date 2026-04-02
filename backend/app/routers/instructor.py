"""Instructor router: JWT-protected course and assignment management."""
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.config import UPLOAD_DIR
from app.core.db import get_db
from app.core.deps import get_current_instructor, to_object_id
from app.schemas.analysis import CreateRunResponse, RunStatusResponse
from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentUpdateRequest,
)
from app.schemas.course import CourseCreateRequest, CourseResponse, CourseUpdateRequest
from app.schemas.public import SubmissionListItem
from app.services.anonymization_service import pseudonymize_student_identifier

router = APIRouter(prefix="/instructor", tags=["instructor"])


# ── Internal helpers ───────────────────────────────


def _generate_assignment_key(db) -> str:
    """Generate a unique random 10-digit assignment key."""
    for _ in range(20):
        key = "".join(str(secrets.randbelow(10)) for _ in range(10))
        if not db.assignments.find_one({"assignmentKey": key}):
            return key
    raise HTTPException(status_code=500, detail="Could not generate unique key")


def _assignment_response(
    doc: dict,
    *,
    submission_count: int = 0,
    analysis_progress: int | None = None,
) -> AssignmentResponse:
    """Map a MongoDB assignment document to the API response model.

    The optional keyword arguments carry aggregated counts that are only
    populated by the list endpoint — single-get and create callers omit them
    and receive the schema defaults (0 / None).
    """
    return AssignmentResponse(
        id=str(doc["_id"]),
        courseId=doc["courseId"],
        title=doc["title"],
        language=doc["language"],
        assignmentKey=doc["assignmentKey"],
        isOpen=doc["isOpen"],
        dueDate=doc.get("dueDate"),
        keyExpiry=doc.get("keyExpiry"),
        autoAnalysis=doc.get("autoAnalysis", False),
        allowLate=doc.get("allowLate", False),
        exclusionCode=doc.get("exclusionCode"),
        createdAt=doc["createdAt"],
        submissionCount=submission_count,
        analysisProgress=analysis_progress,
    )


def _progress_from_status(status: str | None) -> int | None:
    """Map the latest analysis-run status to a 0–100 UI progress integer.

    Mapping rationale:
      completed → 100   (analysis finished successfully)
      running   → 50    (in progress; granular progress not tracked)
      queued    → 0     (waiting to start)
      failed    → 0     (run attempted but errored; not None so the UI shows
                          a progress bar rather than the "--%" placeholder)
      None / unknown → None  (no run has ever been queued)
    """
    if status == "completed":
        return 100
    if status == "running":
        return 50
    if status in ("queued", "failed"):
        return 0
    return None


def _course_response(doc: dict, *, assignment_count: int = 0, analysis_complete_count: int = 0) -> CourseResponse:
    """Map a MongoDB course document to the API response model."""
    return CourseResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        term=doc.get("term"),
        instructorId=doc["instructorId"],
        createdAt=doc["createdAt"],
        assignmentCount=assignment_count,
        analysisCompleteCount=analysis_complete_count,
    )


# ── Courses ────────────────────────────────────────


@router.post("/courses", response_model=CourseResponse, status_code=201)
async def create_course(
    body: CourseCreateRequest,
    current: dict = Depends(get_current_instructor),
):
    """Create a new course for the logged-in instructor."""
    db = get_db()
    doc = {
        "name": body.name,
        "term": body.term,
        "instructorId": current["id"],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = db.courses.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _course_response(doc)


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(current: dict = Depends(get_current_instructor)):
    """List all courses owned by the current instructor, with aggregated counts."""
    db = get_db()
    courses = list(db.courses.find({"instructorId": current["id"]}))
    if not courses:
        return []

    course_id_strs = [str(c["_id"]) for c in courses]

    # ── Batch: assignments for every course in one query ──────────────────
    all_assignments = list(
        db.assignments.find(
            {"courseId": {"$in": course_id_strs}},
            {"_id": 1, "courseId": 1},
        )
    )

    # assignment count per course  +  reverse map aid → course id
    assignment_count_map: dict[str, int] = {}
    assignment_to_course: dict[str, str] = {}
    all_assignment_id_strs: list[str] = []
    for a in all_assignments:
        cid = a["courseId"]
        assignment_count_map[cid] = assignment_count_map.get(cid, 0) + 1
        aid = str(a["_id"])
        all_assignment_id_strs.append(aid)
        assignment_to_course[aid] = cid

    # ── Batch: assignments with ≥1 completed run ──────────────────────────
    analysis_complete_by_course: dict[str, int] = {}
    if all_assignment_id_strs:
        completed_runs = db.analysis_runs.find(
            {
                "assignmentId": {"$in": all_assignment_id_strs},
                "status": "completed",
            },
            {"assignmentId": 1},
        )
        seen_assignment_ids: set[str] = set()
        for run in completed_runs:
            aid = run["assignmentId"]
            if aid not in seen_assignment_ids:
                seen_assignment_ids.add(aid)
                cid = assignment_to_course.get(aid, "")
                if cid:
                    analysis_complete_by_course[cid] = (
                        analysis_complete_by_course.get(cid, 0) + 1
                    )

    return [
        _course_response(
            c,
            assignment_count=assignment_count_map.get(str(c["_id"]), 0),
            analysis_complete_count=analysis_complete_by_course.get(str(c["_id"]), 0),
        )
        for c in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Get a single course by ID, including aggregated counts."""
    db = get_db()
    oid = to_object_id(course_id)
    course = db.courses.find_one({"_id": oid, "instructorId": current["id"]})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_id_str = str(course["_id"])

    assignment_count = db.assignments.count_documents({"courseId": course_id_str})

    # Count assignments that have at least one completed run
    assignment_ids = [
        str(a["_id"])
        for a in db.assignments.find({"courseId": course_id_str}, {"_id": 1})
    ]
    analysis_complete_count = 0
    if assignment_ids:
        completed_run_aids = db.analysis_runs.distinct(
            "assignmentId",
            {"assignmentId": {"$in": assignment_ids}, "status": "completed"},
        )
        analysis_complete_count = len(completed_run_aids)

    return _course_response(
        course,
        assignment_count=assignment_count,
        analysis_complete_count=analysis_complete_count,
    )


@router.patch("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    body: CourseUpdateRequest,
    current: dict = Depends(get_current_instructor),
):
    """Partially update a course (name and/or term)."""
    db = get_db()
    oid = to_object_id(course_id)
    course = db.courses.find_one({"_id": oid, "instructorId": current["id"]})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    updates = body.model_dump(exclude_unset=True)
    if updates:
        db.courses.update_one({"_id": oid}, {"$set": updates})

    updated = db.courses.find_one({"_id": oid})
    return _course_response(updated)


@router.delete("/courses/{course_id}", status_code=204)
async def delete_course(
    course_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Delete a course and cascade-remove all child assignments, submissions,
    analysis runs, similarity results, and uploaded files on disk.

    Follows the same cascade pattern as DELETE /assignments/{assignment_id}
    in instructor_admin.py.
    """
    db = get_db()
    oid = to_object_id(course_id)
    course = db.courses.find_one({"_id": oid, "instructorId": current["id"]})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Cascade per assignment
    assignments = list(db.assignments.find({"courseId": course_id}, {"_id": 1}))
    for a in assignments:
        aid = str(a["_id"])
        db.submissions.delete_many({"assignmentId": aid})
        db.analysis_runs.delete_many({"assignmentId": aid})
        db.similarity_results.delete_many({"assignmentId": aid})
        upload_dir = Path(UPLOAD_DIR) / aid
        if upload_dir.exists() and upload_dir.is_dir():
            shutil.rmtree(upload_dir, ignore_errors=True)

    db.assignments.delete_many({"courseId": course_id})
    db.courses.delete_one({"_id": oid})
    return Response(status_code=204)


# ── Assignments ────────────────────────────────────


@router.post("/assignments", response_model=AssignmentResponse, status_code=201)
async def create_assignment(
    body: AssignmentCreateRequest,
    current: dict = Depends(get_current_instructor),
):
    """Create a new assignment with a unique 10-digit key."""
    db = get_db()

    # The course must belong to this instructor
    course = db.courses.find_one(
        {"_id": to_object_id(body.courseId), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if body.language not in ("java", "c", "cpp"):
        raise HTTPException(status_code=400, detail="Language must be java, c, or cpp")

    key = _generate_assignment_key(db)
    doc = {
        "courseId": body.courseId,
        "title": body.title,
        "language": body.language,
        "assignmentKey": key,
        "isOpen": body.isOpen,
        "dueDate": body.dueDate,
        "keyExpiry": body.keyExpiry,
        "autoAnalysis": body.autoAnalysis,
        "allowLate": body.allowLate,
        "exclusionCode": body.exclusionCode,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    result = db.assignments.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _assignment_response(doc)


@router.patch("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    body: AssignmentUpdateRequest,
    current: dict = Depends(get_current_instructor),
):
    """Partially update an assignment (title, language, isOpen)."""
    db = get_db()
    oid = to_object_id(assignment_id)
    assignment = db.assignments.find_one({"_id": oid})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Ownership check via course
    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your assignment")

    updates = body.model_dump(exclude_unset=True)
    if "language" in updates and updates["language"] not in ("java", "c", "cpp"):
        raise HTTPException(status_code=400, detail="Language must be java, c, or cpp")

    if updates:
        db.assignments.update_one({"_id": oid}, {"$set": updates})

    updated = db.assignments.find_one({"_id": oid})
    return _assignment_response(updated)


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Get a single assignment by ID."""
    db = get_db()
    oid = to_object_id(assignment_id)
    assignment = db.assignments.find_one({"_id": oid})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your assignment")

    return _assignment_response(assignment)


@router.get("/courses/{course_id}/assignments", response_model=list[AssignmentResponse])
async def list_course_assignments(
    course_id: str,
    current: dict = Depends(get_current_instructor),
):
    """List all assignments for a specific course, with aggregated counts."""
    db = get_db()
    oid = to_object_id(course_id)

    # Verify the course belongs to this instructor
    course = db.courses.find_one({"_id": oid, "instructorId": current["id"]})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    assignments = list(db.assignments.find({"courseId": course_id}))
    if not assignments:
        return []

    assignment_id_strs = [str(a["_id"]) for a in assignments]

    # ── Batch: submission count per assignment ────────────────────────────
    sub_pipeline = [
        {"$match": {"assignmentId": {"$in": assignment_id_strs}}},
        {"$group": {"_id": "$assignmentId", "count": {"$sum": 1}}},
    ]
    submission_count_map: dict[str, int] = {
        doc["_id"]: doc["count"]
        for doc in db.submissions.aggregate(sub_pipeline)
    }

    # ── Batch: latest run status per assignment ───────────────────────────
    # Sort by createdAt descending then group to keep only the most recent status.
    run_pipeline = [
        {"$match": {"assignmentId": {"$in": assignment_id_strs}}},
        {"$sort": {"createdAt": -1}},
        {"$group": {"_id": "$assignmentId", "latestStatus": {"$first": "$status"}}},
    ]
    latest_run_map: dict[str, str] = {
        doc["_id"]: doc["latestStatus"]
        for doc in db.analysis_runs.aggregate(run_pipeline)
    }

    return [
        _assignment_response(
            a,
            submission_count=submission_count_map.get(str(a["_id"]), 0),
            analysis_progress=_progress_from_status(latest_run_map.get(str(a["_id"]))),
        )
        for a in assignments
    ]


# ── Submissions ────────────────────────────────────


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=list[SubmissionListItem],
)
async def list_submissions(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """List all submissions for an assignment."""
    db = get_db()
    oid = to_object_id(assignment_id)
    assignment = db.assignments.find_one({"_id": oid})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your assignment")

    return [
        SubmissionListItem(
            submissionId=str(s["_id"]),
            assignmentId=s["assignmentId"],
            studentIdentifier=pseudonymize_student_identifier(s["studentIdentifier"]),
            studentName=pseudonymize_student_identifier(s.get("studentName")) if s.get("studentName") else None,
            submittedAt=s["submittedAt"],
            fileCount=s["fileCount"],
            status=s["status"],
        )
        for s in db.submissions.find({"assignmentId": assignment_id})
    ]


# ── Analysis Runs ──────────────────────────────────


@router.post(
    "/assignments/{assignment_id}/analysis-runs",
    response_model=CreateRunResponse,
    status_code=201,
)
async def create_analysis_run(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Queue a new analysis run for an assignment."""
    db = get_db()
    oid = to_object_id(assignment_id)
    assignment = db.assignments.find_one({"_id": oid})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    course = db.courses.find_one(
        {"_id": ObjectId(assignment["courseId"]), "instructorId": current["id"]}
    )
    if not course:
        raise HTTPException(status_code=403, detail="Not your assignment")

    doc = {
        "assignmentId": assignment_id,
        "status": "queued",
        "algorithmVersion": "v0",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "startedAt": None,
        "finishedAt": None,
        "errorMessage": None,
    }
    result = db.analysis_runs.insert_one(doc)
    return CreateRunResponse(
        runId=str(result.inserted_id),
        status="queued",
        algorithmVersion="v0",
    )


@router.get("/analysis-runs/{run_id}", response_model=RunStatusResponse)
async def get_analysis_run(
    run_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Get the status of an analysis run."""
    db = get_db()
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

    # Pull run-level diagnostics from similarity_results (written by analysis worker)
    sim_doc = db.similarity_results.find_one(
        {"runId": str(run["_id"])},
        {"warnings": 1, "pairsAnalyzed": 1, "pairsFailed": 1},
    )
    run_warnings = (sim_doc or {}).get("warnings") or []
    pairs_analyzed = (sim_doc or {}).get("pairsAnalyzed")
    pairs_failed = (sim_doc or {}).get("pairsFailed")

    return RunStatusResponse(
        runId=str(run["_id"]),
        assignmentId=run["assignmentId"],
        courseId=assignment["courseId"],
        status=run["status"],
        algorithmVersion=run["algorithmVersion"],
        createdAt=run["createdAt"],
        startedAt=run.get("startedAt"),
        finishedAt=run.get("finishedAt"),
        errorMessage=run.get("errorMessage"),
        warnings=run_warnings,
        pairsAnalyzed=pairs_analyzed,
        pairsFailed=pairs_failed,
    )
