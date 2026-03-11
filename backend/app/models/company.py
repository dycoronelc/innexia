from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Company(Base):
    """Modelo para empresas/organizaciones en el sistema multiempresas"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)  # URL-friendly name
    description = Column(Text, nullable=True)
    
    # Configuración visual
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#4D2581")  # Color primario por defecto
    secondary_color = Column(String(7), default="#ED682B")  # Color secundario por defecto
    favicon_url = Column(String(500), nullable=True)
    
    # Información de la empresa
    industry = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(200), nullable=True)
    
    # Ubicación
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC")
    
    # Configuración del plan
    subscription_plan = Column(String(50), default="basic")  # basic, pro, enterprise
    max_users = Column(Integer, default=10)
    max_projects = Column(Integer, default=50)
    max_storage_gb = Column(Integer, default=5)
    
    # Estado
    active = Column(Boolean, default=True)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    users = relationship("User", back_populates="company")
    projects = relationship("Project", back_populates="company")
    categories = relationship("Category", back_populates="company")
    tags = relationship("Tag", back_populates="company")
    locations = relationship("Location", back_populates="company")
    statuses = relationship("Status", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', slug='{self.slug}')>"
