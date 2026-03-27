"""Schemas for instructor similarity-result endpoints."""
from pydantic import BaseModel


class SimilarityResultListItem(BaseModel):
    """One ranked similarity pair for a run."""
    resultId: str
    runId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float


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
    rightSubmissionId: str
    similarityScore: float
    summary: str | None = None


class MatchingRegion(BaseModel):
    """Matched line-region metadata for side-by-side UI."""
    leftStartLine: int
    leftEndLine: int
    rightStartLine: int
    rightEndLine: int


class SimilarityComparisonResponse(BaseModel):
    """Side-by-side payload for one pair."""
    resultId: str
    runId: str
    assignmentId: str
    leftSubmissionId: str
    rightSubmissionId: str
    similarityScore: float
    leftFilePath: str
    rightFilePath: str
    leftCode: str
    rightCode: str
    matchingRegions: list[MatchingRegion]
