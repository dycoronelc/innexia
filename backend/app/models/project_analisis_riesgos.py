"""
Modelos para análisis de riesgos por proyecto (fuente única editable; sincronizados desde agente).
Cabecera: nivel_riesgo_general + recomendaciones; detalle: project_riesgo (uno por riesgo).
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectAnalisisRiesgos(Base):
    __tablename__ = "project_analisis_riesgos"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    nivel_riesgo_general = Column(String(50), nullable=True)
    recomendaciones = Column(JSON, nullable=True)  # array of strings

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectAnalisisRiesgos(project_id={self.project_id})>"


class ProjectRiesgo(Base):
    __tablename__ = "project_riesgo"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)

    categoria = Column(String(100), nullable=True)
    riesgo = Column(String(500), nullable=True)
    probabilidad = Column(String(50), nullable=True)
    impacto = Column(String(50), nullable=True)
    mitigacion = Column(Text, nullable=True)
    orden = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectRiesgo(id={self.id}, project_id={self.project_id})>"
