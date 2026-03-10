"""Schemas for class-list management placeholders."""
from pydantic import BaseModel


class ClassListEntry(BaseModel):
    """Skeleton class-list entry."""
    firstName: str
    lastName: str
    email: str


class ClassListUpsertRequest(BaseModel):
    """Skeleton request for class-list upload/replace."""
    students: list[ClassListEntry]


class ClassListResponse(BaseModel):
    """Skeleton response for class-list reads."""
    courseId: str
    students: list[ClassListEntry]
