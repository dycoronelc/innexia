from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    status: str = Field(default="active", pattern="^(active|inactive|completed)$")

class ProjectCreate(ProjectBase):
    tags: Optional[List[str]] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern="^(active|inactive|completed)$")
    tags: Optional[List[str]] = None

class ProjectInDB(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Project(ProjectInDB):
    tags: List[str] = []
    owner_name: Optional[str] = None

class ProjectWithDetails(Project):
    activities_count: int = 0
    documents_count: int = 0
    has_business_model_canvas: bool = False

