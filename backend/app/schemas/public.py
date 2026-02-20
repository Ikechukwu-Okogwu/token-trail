"""Schemas for public (student-facing) endpoints."""
from pydantic import BaseModel


# ── Validate key ───────────────────────────────────

class ValidateKeyRequest(BaseModel):
    assignmentKey: str


class ValidateKeyAssignmentInfo(BaseModel):
    id: str
    language: str
    isOpen: bool


class ValidateKeyResponse(BaseModel):
    valid: bool
    assignment: ValidateKeyAssignmentInfo | None = None


# ── Submission ─────────────────────────────────────

class SubmissionResponse(BaseModel):
    submissionId: str
    status: str
    fileCount: int
    mergedCreated: bool


class SubmissionListItem(BaseModel):
    """Used by the instructor GET submissions endpoint."""
    submissionId: str
    assignmentId: str
    studentIdentifier: str
    studentName: str | None = None
    submittedAt: str
    fileCount: int
    status: str
