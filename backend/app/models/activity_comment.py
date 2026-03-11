from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class ActivityComment(Base):
    __tablename__ = "activity_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="comments")
    author = relationship("User")
    
    def __repr__(self):
        return f"<ActivityComment(id={self.id}, activity_id={self.activity_id}, author_id={self.author_id})>"
