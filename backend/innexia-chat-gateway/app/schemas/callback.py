from pydantic import BaseModel


class StrategyCallbackRequest(BaseModel):
    request_id: str
    project_id: str | None = None
    status: str
    progress: int | None = None
    current_stage: str | None = None
    completed_at: str | None = None
    engine_version: str | None = None
    workflow_version: str | None = None
    result: dict | None = None
    artifacts: dict | None = None
    metrics: dict | None = None
    error: dict | None = None


class CallbackAckResponse(BaseModel):
    success: bool
    message: str
    request_id: str
