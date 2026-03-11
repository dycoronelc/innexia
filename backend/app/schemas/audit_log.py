from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user import User

class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime
    user: User

    class Config:
        from_attributes = True
