from pydantic import BaseModel, Field


class BaseAPIResponse(BaseModel):
    request_id: str | None = None
    status: str = "completed"


class MessageResponse(BaseModel):
    message: str
