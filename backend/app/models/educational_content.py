from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, DECIMAL, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class ContentType(str, enum.Enum):
    ARTICLE = "article"
    VIDEO = "video"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    COURSE = "course"
    WEBINAR = "webinar"

class ContentSource(str, enum.Enum):
    INTERNAL = "internal"
    RSS_FEED = "rss_feed"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    SPOTIFY = "spotify"
    CUSTOM_API = "custom_api"

class ContentDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    MODERATION = "moderation"

class EducationalContent(Base):
    __tablename__ = "educational_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    content_source = Column(Enum(ContentSource), nullable=False)
    source_url = Column(String(500))
    content_data = Column(JSON)  # Para contenido interno
    difficulty = Column(Enum(ContentDifficulty), default=ContentDifficulty.BEGINNER)
    duration_minutes = Column(Integer)
    author = Column(String(255))
    instructor = Column(String(255))
    thumbnail_url = Column(String(500))
    tags = Column(JSON)
    categories = Column(JSON)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    moderated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderation_notes = Column(Text)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), default=0.00)
    rating_count = Column(Integer, default=0)

    # Relaciones
    creator = relationship("User", foreign_keys=[created_by])
    moderator = relationship("User", foreign_keys=[moderated_by])

