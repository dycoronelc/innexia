"""
Modelo para almacenar la salida del agente IA (n8n) por proyecto.
Estructura compatible con salidaAgente.json e innexia.sql.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectAgentOutput(Base):
    __tablename__ = "project_agent_output"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)
    request_id = Column(String(64), nullable=True, index=True)

    metadata_ = Column("metadata", JSON, nullable=True)
    supervisor_output = Column(Text, nullable=True)
    conversacion = Column(JSON, nullable=True)
    business_model_canvas = Column(JSON, nullable=True)
    estrategia_comercial = Column(JSON, nullable=True)
    roadmap_estrategico = Column(JSON, nullable=True)
    analisis_financiero = Column(JSON, nullable=True)
    analisis_riesgos = Column(JSON, nullable=True)
    veredicto_final = Column(JSON, nullable=True)
    plan_actividades = Column(JSON, nullable=True)
    kanban_json = Column(JSON, nullable=True)
    gantt_json = Column(JSON, nullable=True)
    summary_json = Column(JSON, nullable=True)

    status = Column(String(50), nullable=False, default="completed")
    execution_time_ms = Column(Integer, nullable=True)
    modules_executed = Column(Text, nullable=True)  # JSON array as text
    modules_failed = Column(Text, nullable=True)   # JSON array as text

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectAgentOutput(id={self.id}, project_id={self.project_id})>"
