"""Schemas for assignment exclusion-code placeholders."""
from pydantic import BaseModel


class ExclusionCodeUpsertRequest(BaseModel):
    """Skeleton request for adding/updating exclusion code."""
    exclusionCode: str


class ExclusionCodeResponse(BaseModel):
    """Skeleton response shape for exclusion-code reads."""
    assignmentId: str
    exclusionCode: str | None = None
