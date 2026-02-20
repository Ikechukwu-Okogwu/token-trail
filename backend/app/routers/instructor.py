"""Instructor router: JWT-protected course and assignment management."""
import secrets
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.db import get_db
from app.core.deps import get_current_instructor, to_object_id
from app.schemas.analysis import CreateRunResponse, RunStatusResponse
from app.schemas.assignment import (
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentUpdateRequest,
)
from app.schemas.course import CourseCreateRequest, CourseResponse
from app.schemas.public import SubmissionListItem

router = APIRouter(prefix="/instructor", tags=["instructor"])


def _generate_assignment_key(db) -> str:
    """Generate a unique random 10-digit assignment key."""
    for _ in range(20):
        key = "".join(str(secrets.randbelow(10)) for _ in range(10))
        if not db.assignments.find_one({"assignmentKey": key}):
            return key
    raise HTTPException(status_code=500, detail="Could not generate unique key")


def _assignment_response(doc: dict) -> AssignmentResponse:
    """Map a MongoDB assignment document to the API response model."""
    return AssignmentResponse(
        id=str(doc["_id"]),
        courseId=doc["courseId"],
        title=doc["title"],
        language=doc["language"],
        assignmentKey=doc["assignmentKey"],
        isOpen=doc["isOpen"],
        createdAt=doc["createdAt"],
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
    return CourseResponse(
        id=str(result.inserted_id),
        name=doc["name"],
        term=doc["term"],
        instructorId=doc["instructorId"],
        createdAt=doc["createdAt"],
    )


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(current: dict = Depends(get_current_instructor)):
    """List all courses owned by the current instructor."""
    db = get_db()
    return [
        CourseResponse(
            id=str(c["_id"]),
            name=c["name"],
            term=c.get("term"),
            instructorId=c["instructorId"],
            createdAt=c["createdAt"],
        )
        for c in db.courses.find({"instructorId": current["id"]})
    ]


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
            studentIdentifier=s["studentIdentifier"],
            studentName=s.get("studentName"),
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

    return RunStatusResponse(
        runId=str(run["_id"]),
        assignmentId=run["assignmentId"],
        status=run["status"],
        algorithmVersion=run["algorithmVersion"],
        createdAt=run["createdAt"],
        startedAt=run.get("startedAt"),
        finishedAt=run.get("finishedAt"),
        errorMessage=run.get("errorMessage"),
    )
