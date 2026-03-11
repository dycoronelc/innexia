"""
Modelo para veredicto final por proyecto (fuente única editable; un futuro agente puede re-analizar y actualizar).
Alineado con innexia.sql: confidence, reasons, conditions_to_proceed, executive_summary.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectVeredicto(Base):
    __tablename__ = "project_veredicto"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    decision = Column(String(50), nullable=True)
    confidence = Column(Numeric(5, 2), nullable=True)
    puntuacion_general = Column(Numeric(4, 2), nullable=True)
    fortalezas = Column(JSON, nullable=True)  # array of strings
    debilidades = Column(JSON, nullable=True)  # array of strings
    recomendacion_estrategica = Column(Text, nullable=True)
    siguiente_paso = Column(Text, nullable=True)
    reasons = Column(Text, nullable=True)
    conditions_to_proceed = Column(Text, nullable=True)
    executive_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectVeredicto(project_id={self.project_id})>"
