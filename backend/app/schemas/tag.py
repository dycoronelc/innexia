from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#1976d2"
    active: bool = True

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    name: Optional[str] = None
    color: Optional[str] = None
    active: Optional[bool] = None

class Tag(TagBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
