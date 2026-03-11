from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ProactiveSuggestion(Base):
    __tablename__ = "proactive_suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # 'reminder', 'recommendation', 'alert', 'opportunity'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)  # 1-10, para priorización
    category = Column(String(100), nullable=True)  # 'project', 'activity', 'bmc', 'document', 'learning'
    context_data = Column(JSON, nullable=True)  # Datos contextuales para la sugerencia
    action_url = Column(String(500), nullable=True)  # URL para la acción sugerida
    action_text = Column(String(100), nullable=True)  # Texto del botón de acción
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=True)  # Fecha de expiración
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User")


class SuggestionRule(Base):
    __tablename__ = "suggestion_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False, unique=True)
    rule_type = Column(String(50), nullable=False)  # 'schedule', 'condition', 'event'
    conditions = Column(JSON, nullable=False)  # Condiciones para activar la regla
    suggestion_template = Column(JSON, nullable=False)  # Plantilla de la sugerencia
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserSuggestionPreference(Base):
    __tablename__ = "user_suggestion_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    notification_frequency = Column(String(20), default="daily")  # 'immediate', 'hourly', 'daily', 'weekly'
    preferred_categories = Column(JSON, nullable=True)  # Categorías preferidas
    max_suggestions_per_day = Column(Integer, default=10)
    quiet_hours_start = Column(String(5), default="22:00")  # Hora de inicio de silencio
    quiet_hours_end = Column(String(5), default="08:00")  # Hora de fin de silencio
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    user = relationship("User")

