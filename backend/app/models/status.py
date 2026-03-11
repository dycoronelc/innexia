from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Status(Base):
    """Modelo para estados de proyectos"""
    __tablename__ = "statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True, default="#6B7280")  # Color en formato HEX
    icon = Column(String(50), nullable=True)  # Nombre del icono
    is_final = Column(Boolean, default=False)  # Si es un estado final (completado, cancelado)
    order = Column(Integer, default=0)  # Orden para mostrar en listas
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    company = relationship("Company", back_populates="statuses")
    
    def __repr__(self):
        return f"<Status(id={self.id}, name='{self.name}', company_id={self.company_id})>"
