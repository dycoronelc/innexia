"""
Modelo para análisis financiero por proyecto (fuente única editable; sincronizado desde agente).
Alineado con innexia.sql: incluye campos extra para n8n (costo_operativo_mensual, payback_meses, etc.).
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectAnalisisFinanciero(Base):
    __tablename__ = "project_analisis_financiero"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    inversion_inicial = Column(JSON, nullable=True)
    proyecciones_3_anos = Column(JSON, nullable=True)
    metricas_clave = Column(JSON, nullable=True)
    viabilidad_financiera = Column(String(50), nullable=True)
    costo_operativo_mensual = Column(Numeric(14, 2), nullable=True)
    modelo_ingresos = Column(String(100), nullable=True)
    ingreso_mensual_esperado = Column(Numeric(14, 2), nullable=True)
    margen_estimado = Column(Numeric(8, 2), nullable=True)
    payback_meses = Column(Integer, nullable=True)
    observaciones = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectAnalisisFinanciero(project_id={self.project_id})>"
