from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Category(Base):
    """Modelo para categorías de proyectos"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True, default="#4D2581")  # Color en formato HEX
    icon = Column(String(50), nullable=True)  # Nombre del icono (ej: "business", "technology")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    company = relationship("Company", back_populates="categories")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', company_id={self.company_id})>"
