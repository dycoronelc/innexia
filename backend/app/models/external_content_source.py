from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class SourceType(str, enum.Enum):
    RSS_FEED = "rss_feed"
    YOUTUBE_CHANNEL = "youtube_channel"
    VIMEO_CHANNEL = "vimeo_channel"
    SPOTIFY_SHOW = "spotify_show"
    CUSTOM_API = "custom_api"

class ExternalContentSource(Base):
    __tablename__ = "external_content_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    source_url = Column(String(500), nullable=False)
    api_key = Column(String(255))
    api_secret = Column(String(255))
    refresh_interval_minutes = Column(Integer, default=60)
    last_sync_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    auto_import = Column(Boolean, default=False)
    category_mapping = Column(JSON)  # Mapeo de categorías externas a internas
    tag_mapping = Column(JSON)  # Mapeo de tags externos a internos
    content_filters = Column(JSON)  # Filtros para contenido específico
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relaciones
    creator = relationship("User", foreign_keys=[created_by])

