"""
Modelo para estrategia comercial por proyecto (fuente única editable; sincronizada desde agente).
"""
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectEstrategiaComercial(Base):
    __tablename__ = "project_estrategia_comercial"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    analisis_mercado = Column(JSON, nullable=True)
    estrategia_precios = Column(JSON, nullable=True)
    estrategia_marketing = Column(JSON, nullable=True)
    estrategia_ventas = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectEstrategiaComercial(project_id={self.project_id})>"
