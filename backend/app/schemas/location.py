from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    coordinates: Optional[str] = None
    timezone: Optional[str] = None
    active: bool = True

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    active: Optional[bool] = None

class Location(LocationBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
