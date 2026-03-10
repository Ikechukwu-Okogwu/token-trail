"""Shared response schemas used across multiple routers."""
from pydantic import BaseModel


class NotImplementedResponse(BaseModel):
    status: str
    feature: str
    message: str
