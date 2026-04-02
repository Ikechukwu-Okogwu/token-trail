"""Schemas for assignment endpoints."""
from typing import Literal

from pydantic import BaseModel

SUPPORTED_LANGUAGES = Literal["java", "c", "cpp"]


class AssignmentCreateRequest(BaseModel):
    courseId: str
    title: str
    language: SUPPORTED_LANGUAGES
    isOpen: bool = True
    dueDate: str | None = None
    keyExpiry: str | None = None
    autoAnalysis: bool = False
    allowLate: bool = False
    exclusionCode: str | None = None


class AssignmentUpdateRequest(BaseModel):
    title: str | None = None
    language: SUPPORTED_LANGUAGES | None = None
    isOpen: bool | None = None
    dueDate: str | None = None
    keyExpiry: str | None = None
    autoAnalysis: bool | None = None
    allowLate: bool | None = None
    exclusionCode: str | None = None


class AssignmentResponse(BaseModel):
    id: str
    courseId: str
    title: str
    language: str
    assignmentKey: str
    isOpen: bool
    dueDate: str | None = None
    keyExpiry: str | None = None
    autoAnalysis: bool = False
    allowLate: bool = False
    exclusionCode: str | None = None
    createdAt: str
    # Aggregated counts — populated by the assignment-list endpoint.
    # Default to 0 / None so single-get and create responses stay well-typed.
    submissionCount: int = 0
    # 0–100 integer, or None when no analysis run has ever been queued.
    analysisProgress: int | None = None
