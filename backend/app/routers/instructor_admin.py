"""Instructor admin placeholder routes (JWT required)."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.deps import get_current_instructor
from app.schemas.class_list import ClassListUpsertRequest
from app.schemas.common import NotImplementedResponse
from app.schemas.exclusion import ExclusionCodeUpsertRequest

router = APIRouter(prefix="/instructor", tags=["instructor-admin"])


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


@router.post("/assignments/{assignment_id}/regenerate-key", response_model=NotImplementedResponse)
async def regenerate_assignment_key(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: regenerate assignment key."""
    _ = (assignment_id, current)
    return _not_implemented("regenerate_assignment_key")


@router.post("/assignments/{assignment_id}/expire-key", response_model=NotImplementedResponse)
async def expire_assignment_key(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: revoke/expire assignment key."""
    _ = (assignment_id, current)
    return _not_implemented("expire_assignment_key")


@router.get(
    "/assignments/{assignment_id}/submissions/download",
    response_model=NotImplementedResponse,
)
async def download_assignment_submissions_zip(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: bulk-download submissions as a ZIP."""
    _ = (assignment_id, current)
    return _not_implemented("download_submissions_zip")


@router.delete("/assignments/{assignment_id}/submissions", response_model=NotImplementedResponse)
async def delete_assignment_submissions(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: delete all submissions for an assignment."""
    _ = (assignment_id, current)
    return _not_implemented("delete_assignment_submissions")


@router.delete("/assignments/{assignment_id}", response_model=NotImplementedResponse)
async def delete_assignment(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: delete one assignment."""
    _ = (assignment_id, current)
    return _not_implemented("delete_assignment")


@router.get("/assignments/{assignment_id}/exclusion-code", response_model=NotImplementedResponse)
async def get_exclusion_code(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: read assignment exclusion code."""
    _ = (assignment_id, current)
    return _not_implemented("get_exclusion_code")


@router.put("/assignments/{assignment_id}/exclusion-code", response_model=NotImplementedResponse)
async def upsert_exclusion_code(
    assignment_id: str,
    body: ExclusionCodeUpsertRequest,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: add/update assignment exclusion code."""
    _ = (assignment_id, body, current)
    return _not_implemented("upsert_exclusion_code")


@router.delete(
    "/assignments/{assignment_id}/exclusion-code",
    response_model=NotImplementedResponse,
)
async def delete_exclusion_code(
    assignment_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: remove assignment exclusion code."""
    _ = (assignment_id, current)
    return _not_implemented("delete_exclusion_code")


@router.get("/courses/{course_id}/class-list", response_model=NotImplementedResponse)
async def get_class_list(
    course_id: str,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: read course class list."""
    _ = (course_id, current)
    return _not_implemented("get_class_list")


@router.put("/courses/{course_id}/class-list", response_model=NotImplementedResponse)
async def upsert_class_list(
    course_id: str,
    body: ClassListUpsertRequest,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: upload/replace class list for course."""
    _ = (course_id, body, current)
    return _not_implemented("upsert_class_list")


@router.post("/courses/{course_id}/class-list", response_model=NotImplementedResponse)
async def create_class_list(
    course_id: str,
    body: ClassListUpsertRequest,
    current: dict = Depends(get_current_instructor),
):
    """Placeholder: create class list for course."""
    _ = (course_id, body, current)
    return _not_implemented("create_class_list")
