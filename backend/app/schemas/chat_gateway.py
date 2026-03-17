"""
Schemas para el chat gateway (flujo submit → n8n → callback).
Compatible con innexia-chat-gateway y flujos n8n.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ChatSubmitRequest(BaseModel):
    user_id: Optional[str] = None
    project_id: Optional[int] = None
    message: str = Field(..., min_length=1)
    analysis_type: str = Field(default="full_strategy")
    language_code: str = Field(default="es")
    organization_name: Optional[str] = "Innexia"
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSubmitResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    message: str


class ChatStatusResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    progress: Optional[int] = None
    current_stage: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ChatResultResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    executive_summary: Optional[str] = None


class StrategyCallbackRequest(BaseModel):
    request_id: str
    project_id: Optional[int] = None
    status: str
    progress: Optional[int] = None
    current_stage: Optional[str] = None
    completed_at: Optional[str] = None
    engine_version: Optional[str] = None
    workflow_version: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class CallbackAckResponse(BaseModel):
    success: bool
    message: str
    request_id: str
