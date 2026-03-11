"""
Schemas para la salida del agente IA (n8n) por proyecto.
Compatible con la estructura de salidaAgente.json.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime


class ProjectAgentOutputBase(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    conversacion: Optional[Dict[str, Any]] = None
    business_model_canvas: Optional[Dict[str, Any]] = None
    estrategia_comercial: Optional[Dict[str, Any]] = None
    roadmap_estrategico: Optional[Dict[str, Any]] = None
    analisis_financiero: Optional[Dict[str, Any]] = None
    analisis_riesgos: Optional[Dict[str, Any]] = None
    veredicto_final: Optional[Dict[str, Any]] = None
    plan_actividades: Optional[Dict[str, Any]] = None


class ProjectAgentOutputCreate(ProjectAgentOutputBase):
    """Payload completo que envía n8n / frontend (salidaAgente.json)."""
    pass


class ProjectAgentOutputUpdate(BaseModel):
    """Actualización parcial."""
    metadata: Optional[Dict[str, Any]] = None
    conversacion: Optional[Dict[str, Any]] = None
    business_model_canvas: Optional[Dict[str, Any]] = None
    estrategia_comercial: Optional[Dict[str, Any]] = None
    roadmap_estrategico: Optional[Dict[str, Any]] = None
    analisis_financiero: Optional[Dict[str, Any]] = None
    analisis_riesgos: Optional[Dict[str, Any]] = None
    veredicto_final: Optional[Dict[str, Any]] = None
    plan_actividades: Optional[Dict[str, Any]] = None


class ProjectAgentOutputResponse(ProjectAgentOutputBase):
    id: int
    project_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateProjectFromAgentPayload(BaseModel):
    """
    Crea un proyecto nuevo a partir de la salida del agente.
    Incluye nombre/descripción opcionales (si no se envían, se infieren del JSON).
    """
    payload: Dict[str, Any] = Field(..., description="Objeto completo salidaAgente.json")
    name: Optional[str] = Field(None, description="Nombre del proyecto (opcional)")
    description: Optional[str] = Field(None, description="Descripción (opcional)")
    category_id: Optional[int] = None
    location_id: Optional[int] = None
