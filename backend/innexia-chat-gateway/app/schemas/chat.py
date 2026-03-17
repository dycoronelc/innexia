from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatSubmitRequest(BaseModel):
    user_id: str | None = None
    project_id: str | None = None
    message: str = Field(..., min_length=3)
    analysis_type: str = "full_strategy"
    language_code: str = "es"
    organization_name: str | None = "Innexia"
    callback_url: str | None = None
    metadata: dict[str, Any] | None = None


class ChatSubmitResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    message: str


class ChatStatusResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    progress: int
    current_stage: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class ChatResultResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    result: dict[str, Any] | None = None
    executive_summary: str | None = None
