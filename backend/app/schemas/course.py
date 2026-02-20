"""Schemas for course endpoints."""
from pydantic import BaseModel


class CourseCreateRequest(BaseModel):
    name: str
    term: str | None = None


class CourseResponse(BaseModel):
    id: str
    name: str
    term: str | None = None
    instructorId: str
    createdAt: str
