from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    company = relationship("Company", back_populates="projects")
    owner = relationship("User", back_populates="projects")
    category = relationship("Category")
    location = relationship("Location")
    status = relationship("Status")
    activities = relationship("ProjectActivity", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("ProjectDocument", back_populates="project", cascade="all, delete-orphan")
    business_model_canvas = relationship("BusinessModelCanvas", back_populates="project", uselist=False, cascade="all, delete-orphan")
    tags = relationship("ProjectTag", back_populates="project", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", overlaps="project")
    document_logs = relationship("DocumentGenerationLog", overlaps="project")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status_id={self.status_id})>"

class ProjectTag(Base):
    __tablename__ = "project_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="tags")
    tag = relationship("Tag")
    
    def __repr__(self):
        return f"<ProjectTag(id={self.id}, project_id={self.project_id}, tag_id={self.tag_id})>"

