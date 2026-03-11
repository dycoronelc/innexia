from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Tag(Base):
    """Modelo para etiquetas de proyectos"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True, default="#ED682B")  # Color en formato HEX
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    company = relationship("Company", back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', company_id={self.company_id})>"
