"""Instructor similarity-report placeholder routes (JWT required)."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.deps import get_current_instructor

router = APIRouter(prefix="/instructor", tags=["instructor-similarity"])


def _not_implemented(feature: str) -> JSONResponse:
    """Return a standard skeleton placeholder response."""
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "feature": feature,
            "message": "Skeleton placeholder endpoint. Implementation planned in future sprint.",
        },
    )


@router.get("/analysis-runs/{run_id}/similarity-results")
async def get_ranked_similarity_results(
    run_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: ranked similarity list for one analysis run."""
    _ = (run_id, current)
    return _not_implemented("ranked_similarity_results")


@router.get("/similarity-results/{result_id}")
async def get_similarity_pair_detail(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: pair drill-down details."""
    _ = (result_id, current)
    return _not_implemented("similarity_pair_detail")


@router.get("/similarity-results/{result_id}/comparison")
async def get_similarity_side_by_side_comparison(
    result_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: side-by-side highlighted comparison payload."""
    _ = (result_id, current)
    return _not_implemented("similarity_side_by_side_comparison")
