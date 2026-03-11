from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# CompanyBase eliminado ya que no es necesario

class CompanyCreate(BaseModel):
    """Esquema para crear empresa"""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la empresa")
    slug: str = Field(..., min_length=1, max_length=100, description="Slug único de la empresa")
    description: Optional[str] = Field(None, description="Descripción de la empresa")
    
    # Configuración visual
    logo_url: Optional[str] = Field(None, description="URL del logo de la empresa")
    primary_color: Optional[str] = Field("#4D2581", description="Color primario de la empresa")
    secondary_color: Optional[str] = Field("#ED682B", description="Color secundario de la empresa")
    favicon_url: Optional[str] = Field(None, description="URL del favicon de la empresa")
    
    # Información de la empresa
    industry: Optional[str] = Field(None, max_length=100, description="Industria de la empresa")
    website: Optional[str] = Field(None, max_length=200, description="Sitio web de la empresa")
    phone: Optional[str] = Field(None, max_length=50, description="Teléfono de la empresa")
    email: Optional[str] = Field(None, max_length=200, description="Email de la empresa")
    
    # Ubicación
    country: Optional[str] = Field(None, max_length=100, description="País de la empresa")
    state: Optional[str] = Field(None, max_length=100, description="Estado/Provincia de la empresa")
    city: Optional[str] = Field(None, max_length=100, description="Ciudad de la empresa")
    address: Optional[str] = Field(None, description="Dirección de la empresa")
    timezone: Optional[str] = Field("UTC", max_length=50, description="Zona horaria de la empresa")
    
    # Configuración del plan
    subscription_plan: Optional[str] = Field("basic", max_length=50, description="Plan de suscripción")
    max_users: Optional[int] = Field(10, ge=1, description="Máximo número de usuarios")
    max_projects: Optional[int] = Field(50, ge=1, description="Máximo número de proyectos")
    max_storage_gb: Optional[int] = Field(5, ge=1, description="Almacenamiento máximo en GB")

class CompanyUpdate(BaseModel):
    """Esquema para actualizar empresa"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    favicon_url: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    subscription_plan: Optional[str] = Field(None, max_length=50)
    max_users: Optional[int] = Field(None, ge=1)
    max_projects: Optional[int] = Field(None, ge=1)
    max_storage_gb: Optional[int] = Field(None, ge=1)

class CompanyResponse(BaseModel):
    """Esquema para respuesta de empresa"""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    
    # Configuración visual
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    favicon_url: Optional[str] = None
    
    # Información de la empresa
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Ubicación
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    timezone: str
    
    # Configuración del plan
    subscription_plan: str
    max_users: int
    max_projects: int
    max_storage_gb: int
    
    # Estado
    active: bool
    trial_ends_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CompanySummary(BaseModel):
    """Esquema resumido para empresa"""
    id: int
    name: str
    slug: str
    primary_color: str
    secondary_color: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    
    class Config:
        from_attributes = True
