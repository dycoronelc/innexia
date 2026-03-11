from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StatusBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#1976d2"
    active: bool = True

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    name: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None

class Status(StatusBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
