from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)  # create, update, delete, login, logout
    entity_type = Column(String(100), nullable=False)  # user, project, activity, document
    entity_id = Column(String(100), nullable=True)  # ID de la entidad afectada
    details = Column(Text, nullable=True)  # Detalles adicionales de la acción
    ip_address = Column(String(45), nullable=True)  # IPv4 o IPv6
    user_agent = Column(Text, nullable=True)  # User agent del navegador
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}', entity_type='{self.entity_type}')>"

