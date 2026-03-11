from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class AgentMemory(Base):
    __tablename__ = "agent_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    memory_type = Column(String(50), nullable=False)  # 'conversation', 'context', 'preferences', 'state'
    key = Column(String(255), nullable=False)
    value = Column(JSON, nullable=False)
    importance = Column(Integer, default=1)  # 1-10, para priorización de memoria
    expires_at = Column(DateTime, nullable=True)  # Para memoria temporal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User", overlaps="agent_memories")


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    session_type = Column(String(50), nullable=True, default="general")
    status = Column(String(20), nullable=True, default="active")
    context_data = Column(JSON, nullable=True)
    metadata_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", overlaps="agent_memories")
    project = relationship("Project")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    message_type = Column(String(50), nullable=False)  # 'user', 'agent', 'system'
    content = Column(Text, nullable=False)
    metadata_info = Column(JSON, nullable=True)  # Información adicional del mensaje
    intent_detected = Column(String(100), nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    session = relationship("ConversationSession")


class UserContext(Base):
    __tablename__ = "user_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    current_project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    expertise_level = Column(String(50), default="beginner")  # beginner, intermediate, expert
    business_sector = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="es")
    notification_preferences = Column(JSON, nullable=True)
    learning_goals = Column(JSON, nullable=True)
    last_interaction = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", overlaps="agent_memories")
    current_project = relationship("Project")
