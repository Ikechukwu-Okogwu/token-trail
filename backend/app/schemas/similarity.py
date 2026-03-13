"""Schemas for instructor similarity-report placeholders."""
from pydantic import BaseModel


class SimilarityResultListItem(BaseModel):
    """Skeleton ranked-list row."""
    resultId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float


class SimilarityResultsResponse(BaseModel):
    """Skeleton ranked-results response."""
    runId: str
    results: list[SimilarityResultListItem]


class SimilarityPairDetailResponse(BaseModel):
    """Skeleton pair-detail response."""
    resultId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float
    summary: str | None = None


class MatchingRegion(BaseModel):
    """Skeleton highlighted match segment."""
    leftStartLine: int
    leftEndLine: int
    rightStartLine: int
    rightEndLine: int


class SimilarityComparisonResponse(BaseModel):
    """Skeleton side-by-side comparison response."""
    resultId: str
    leftFilePath: str
    rightFilePath: str
    matchingRegions: list[MatchingRegion]
