"""Schemas for assignment endpoints."""
from pydantic import BaseModel


class AssignmentCreateRequest(BaseModel):
    courseId: str
    title: str
    language: str          # "java", "c", or "cpp"
    isOpen: bool = True


class AssignmentUpdateRequest(BaseModel):
    title: str | None = None
    language: str | None = None
    isOpen: bool | None = None


class AssignmentResponse(BaseModel):
    id: str
    courseId: str
    title: str
    language: str
    assignmentKey: str
    isOpen: bool
    createdAt: str
