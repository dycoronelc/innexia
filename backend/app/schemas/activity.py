from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectActivityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="todo", pattern="^(todo|in-progress|review|completed)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    start_date: datetime
    due_date: datetime

class ProjectActivityCreate(ProjectActivityBase):
    project_id: int
    assignee_ids: list[int] = Field(default_factory=list, description="Lista de IDs de usuarios asignados")

class ProjectActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in-progress|review|completed)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assignee_ids: Optional[list[int]] = Field(None, description="Lista de IDs de usuarios asignados")

class ProjectActivityInDB(ProjectActivityBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectActivity(ProjectActivityInDB):
    assignee_name: Optional[str] = None
    project_name: Optional[str] = None

