from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    ARTICLE = "article"
    VIDEO = "video"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    COURSE = "course"
    WEBINAR = "webinar"

class ContentSource(str, Enum):
    INTERNAL = "internal"
    RSS_FEED = "rss_feed"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    SPOTIFY = "spotify"
    CUSTOM_API = "custom_api"

class ContentDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    MODERATION = "moderation"

# Base schema
class EducationalContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: ContentType
    content_source: ContentSource
    source_url: Optional[str] = None
    content_data: Optional[Dict[str, Any]] = None
    difficulty: ContentDifficulty = ContentDifficulty.BEGINNER
    duration_minutes: Optional[int] = None
    author: Optional[str] = None
    instructor: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: Optional[List[str]] = []
    categories: Optional[List[str]] = []

# Schema para crear
class EducationalContentCreate(EducationalContentBase):
    status: Optional[ContentStatus] = ContentStatus.DRAFT

# Schema para actualizar
class EducationalContentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    content_source: Optional[ContentSource] = None
    source_url: Optional[str] = None
    content_data: Optional[Dict[str, Any]] = None
    difficulty: Optional[ContentDifficulty] = None
    duration_minutes: Optional[int] = None
    author: Optional[str] = None
    instructor: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    status: Optional[ContentStatus] = None

# Schema para respuesta
class EducationalContentResponse(EducationalContentBase):
    id: int
    status: ContentStatus
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: int
    moderated_by: Optional[int] = None
    moderation_notes: Optional[str] = None
    view_count: int
    like_count: int
    bookmark_count: int
    rating: float
    rating_count: int

    class Config:
        from_attributes = True

# Schema para listado
class EducationalContentList(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    content_type: ContentType
    content_source: Optional[ContentSource] = None
    source_url: Optional[str] = None
    difficulty: ContentDifficulty
    duration_minutes: Optional[int] = None
    author: Optional[str] = None
    instructor: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: Optional[List[str]] = []
    categories: Optional[List[str]] = []
    status: ContentStatus
    created_at: datetime
    view_count: int
    like_count: int
    bookmark_count: int
    rating: float

    class Config:
        from_attributes = True

# Schema para filtros
class EducationalContentFilters(BaseModel):
    search: Optional[str] = None
    content_type: Optional[ContentType] = None
    difficulty: Optional[ContentDifficulty] = None
    status: Optional[ContentStatus] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    created_by: Optional[int] = None
    limit: int = 20
    offset: int = 0

