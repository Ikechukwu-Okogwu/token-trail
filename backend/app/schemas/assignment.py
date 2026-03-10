"""Schemas for assignment endpoints."""
from pydantic import BaseModel


class AssignmentCreateRequest(BaseModel):
    courseId: str
    title: str
    language: str          # "java", "c", or "cpp"
    isOpen: bool = True
    dueDate: str | None = None
    keyExpiry: str | None = None
    autoAnalysis: bool = False
    allowLate: bool = False
    exclusionCode: str | None = None


class AssignmentUpdateRequest(BaseModel):
    title: str | None = None
    language: str | None = None
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
