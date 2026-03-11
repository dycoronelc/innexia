from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectDocumentBase(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectDocumentCreate(ProjectDocumentBase):
    project_id: int

class ProjectDocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectDocumentInDB(ProjectDocumentBase):
    id: int
    original_filename: str
    file_path: str
    file_type: Optional[str] = None
    file_size: int
    project_id: int
    uploader_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectDocument(ProjectDocumentInDB):
    uploader_name: Optional[str] = None
    project_name: Optional[str] = None

class ProjectDocumentUpload(BaseModel):
    project_id: int
    filename: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

