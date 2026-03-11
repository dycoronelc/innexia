from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class ProjectActivity(Base):
    __tablename__ = "project_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="todo", nullable=False)  # todo, in-progress, review, completed
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="activities")
    assignees = relationship("ActivityAssignee", back_populates="activity", cascade="all, delete-orphan")
    tags = relationship("ActivityTag", back_populates="activity", cascade="all, delete-orphan")
    comments = relationship("ActivityComment", back_populates="activity", cascade="all, delete-orphan")
    checklists = relationship("ActivityChecklist", back_populates="activity", cascade="all, delete-orphan")
    attachments = relationship("ActivityAttachment", back_populates="activity", cascade="all, delete-orphan")
    labels = relationship("ActivityLabel", back_populates="activity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProjectActivity(id={self.id}, title='{self.title}', status='{self.status}')>"

class ActivityAssignee(Base):
    __tablename__ = "activity_assignees"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="assignees")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ActivityAssignee(id={self.id}, activity_id={self.activity_id}, user_id={self.user_id})>"

class ActivityTag(Base):
    __tablename__ = "activity_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="tags")
    tag = relationship("Tag")
    
    def __repr__(self):
        return f"<ActivityTag(id={self.id}, activity_id={self.activity_id}, tag_id={self.tag_id})>"

class ActivityLabel(Base):
    __tablename__ = "activity_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="labels")
    category = relationship("Category")
    
    def __repr__(self):
        return f"<ActivityLabel(id={self.id}, activity_id={self.activity_id}, category_id={self.category_id})>"

