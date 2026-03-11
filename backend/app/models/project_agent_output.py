"""
Modelo para almacenar la salida del agente IA (n8n) por proyecto.
Estructura compatible con salidaAgente.json.
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class ProjectAgentOutput(Base):
    __tablename__ = "project_agent_output"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    metadata_ = Column("metadata", JSON, nullable=True)
    conversacion = Column(JSON, nullable=True)
    business_model_canvas = Column(JSON, nullable=True)
    estrategia_comercial = Column(JSON, nullable=True)
    roadmap_estrategico = Column(JSON, nullable=True)
    analisis_financiero = Column(JSON, nullable=True)
    analisis_riesgos = Column(JSON, nullable=True)
    veredicto_final = Column(JSON, nullable=True)
    plan_actividades = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectAgentOutput(id={self.id}, project_id={self.project_id})>"
