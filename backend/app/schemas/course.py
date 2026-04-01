"""Schemas for course endpoints."""
from pydantic import BaseModel


class CourseCreateRequest(BaseModel):
    name: str
    term: str | None = None


class CourseUpdateRequest(BaseModel):
    name: str | None = None
    term: str | None = None


class CourseResponse(BaseModel):
    id: str
    name: str
    term: str | None = None
    instructorId: str
    createdAt: str
    # Aggregated counts — populated by the list and single-get endpoints.
    # Default to 0 so create/patch responses remain well-typed without extra queries.
    assignmentCount: int = 0
    analysisCompleteCount: int = 0
