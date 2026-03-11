from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class EducationalCategory(Base):
    __tablename__ = "educational_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(7))  # Hex color
    parent_id = Column(Integer, ForeignKey("educational_categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relaciones
    parent = relationship("EducationalCategory", remote_side=[id], overlaps="parent")
    children = relationship("EducationalCategory", overlaps="parent")

