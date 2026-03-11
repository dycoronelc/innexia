from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class ActivityChecklist(Base):
    __tablename__ = "activity_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="checklists")
    items = relationship("ActivityChecklistItem", back_populates="checklist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ActivityChecklist(id={self.id}, activity_id={self.activity_id}, title='{self.title}')>"

class ActivityChecklistItem(Base):
    __tablename__ = "activity_checklist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    checklist_id = Column(Integer, ForeignKey("activity_checklists.id"), nullable=False)
    content = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    checklist = relationship("ActivityChecklist", back_populates="items")
    completed_by = relationship("User")
    
    def __repr__(self):
        return f"<ActivityChecklistItem(id={self.id}, checklist_id={self.checklist_id}, content='{self.content}', completed={self.completed})>"
