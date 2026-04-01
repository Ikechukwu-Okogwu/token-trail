"""Schemas for instructor similarity-result endpoints."""
from pydantic import BaseModel, Field


class SimilarityResultListItem(BaseModel):
    """One ranked similarity pair for a run."""
    resultId: str
    runId: str
    assignmentId: str
    leftSubmissionId: str
    leftStudentIdentifier: str
    leftStudentName: str | None = None
    rightSubmissionId: str
    rightStudentIdentifier: str
    rightStudentName: str | None = None
    similarityScore: float
    confidence: float = 0.0
    largestBlockSize: int = 0


class SimilarityResultsResponse(BaseModel):
    """Ranked similarity results for one analysis run."""
    runId: str
    assignmentId: str
    results: list[SimilarityResultListItem]


class SimilarityPairDetailResponse(BaseModel):
    """Detailed similarity-pair payload."""
    resultId: str
    runId: str
    assignmentId: str
    leftSubmissionId: str
    leftStudentIdentifier: str
    leftStudentName: str | None = None
    rightSubmissionId: str
    rightStudentIdentifier: str
    rightStudentName: str | None = None
    similarityScore: float
    summary: str | None = None


class MatchingRegion(BaseModel):
    """Matched line-region metadata for side-by-side UI."""
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
    """Side-by-side payload for one pair."""
    resultId: str
    runId: str
    assignmentId: str
    leftSubmissionId: str
    leftStudentIdentifier: str
    leftStudentName: str | None = None
    rightSubmissionId: str
    rightStudentIdentifier: str
    rightStudentName: str | None = None
    similarityScore: float
    leftFilePath: str
    rightFilePath: str
    leftCode: str
    rightCode: str
    matchingRegions: list[MatchingRegion]
    excludedRegions: list[ExcludedRegion]
    summary: str
    confidence: float
    snippets: list[str]
