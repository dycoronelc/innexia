from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # admin, user, super_admin
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    company = relationship("Company", back_populates="users")
    projects = relationship("Project", back_populates="owner")
    documents = relationship("ProjectDocument", back_populates="uploader")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Nuevas relaciones con actividades
    activity_assignments = relationship("ActivityAssignee", back_populates="user")
    activity_comments = relationship("ActivityComment", back_populates="author")
    activity_attachments = relationship("ActivityAttachment", back_populates="uploader")
    checklist_item_completions = relationship("ActivityChecklistItem", back_populates="completed_by")
    
    # Relaciones para memoria del agente
    agent_memories = relationship("AgentMemory", overlaps="user")
    conversation_sessions = relationship("ConversationSession", overlaps="user")
    context = relationship("UserContext", uselist=False, overlaps="user")
    
    # Relaciones para análisis de datos
    analytics = relationship("UserAnalytics", uselist=False, overlaps="user")
    recommendations = relationship("RecommendationEngine", overlaps="user")
    analytics_events = relationship("AnalyticsEvent", overlaps="user")
    learning_paths = relationship("LearningPath", overlaps="user")
    
    # Relaciones para gestión avanzada de estado de conversaciones
    conversation_states = relationship("ConversationState")
    
    # Relaciones para documentos generados
    generated_documents = relationship("GeneratedDocument", overlaps="user")
    document_generation_logs = relationship("DocumentGenerationLog", overlaps="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', company_id={self.company_id})>"

