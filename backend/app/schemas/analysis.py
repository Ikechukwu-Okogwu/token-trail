"""Schemas for analysis-run endpoints."""
from pydantic import BaseModel


class CreateRunResponse(BaseModel):
    runId: str
    status: str
    algorithmVersion: str


class RunStatusResponse(BaseModel):
    runId: str
    assignmentId: str
    courseId: str
    status: str
    algorithmVersion: str
    createdAt: str
    startedAt: str | None = None
    finishedAt: str | None = None
    errorMessage: str | None = None
