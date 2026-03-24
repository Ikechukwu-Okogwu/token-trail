"""Schemas for instructor similarity-report responses."""
from pydantic import BaseModel, Field


class SimilarityResultListItem(BaseModel):
    """Ranked-list row."""
    resultId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float
    confidence: float = 0.0
    largestBlockSize: int = 0


class SimilarityResultsResponse(BaseModel):
    """Skeleton ranked-results response."""
    runId: str
    results: list[SimilarityResultListItem]


class SimilarityPairDetailResponse(BaseModel):
    """Pair-detail response."""
    resultId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float
    summary: str | None = None


class MatchingRegion(BaseModel):
    """Highlighted matching segment between two submissions."""
    leftStartLine: int
    leftEndLine: int
    rightStartLine: int
    rightEndLine: int
    score: float
    evidenceType: str = Field(default="winnowing_group")
    snippet: str


class ExcludedRegion(BaseModel):
    """Line-range segment excluded from highlight rendering."""
    leftStartLine: int | None = None
    leftEndLine: int | None = None
    rightStartLine: int | None = None
    rightEndLine: int | None = None
    evidenceType: str = Field(default="non_match")
    reason: str | None = None


class SimilarityComparisonResponse(BaseModel):
    """Side-by-side highlighted comparison response."""
    resultId: str
    leftFilePath: str
    rightFilePath: str
    matchingRegions: list[MatchingRegion]
    excludedRegions: list[ExcludedRegion]
    summary: str
    confidence: float
    snippets: list[str]
