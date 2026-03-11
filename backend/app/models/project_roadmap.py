"""
Modelo para roadmap estratégico por proyecto (fuente única editable; sincronizado desde agente).
Alineado con innexia.sql: milestones, assumptions, project_start_date, project_end_date, gantt_json.
"""
from sqlalchemy import Column, Integer, Text, Date, DateTime
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

from ..database import Base


class ProjectRoadmap(Base):
    __tablename__ = "project_roadmap"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False, unique=True)

    cronograma_total_meses = Column(Integer, nullable=True)
    fases = Column(JSON, nullable=True)  # array of {fase, duracion_meses, hitos[], recursos_necesarios[]}
    milestones = Column(Text, nullable=True)
    assumptions = Column(Text, nullable=True)
    project_start_date = Column(Date, nullable=True)
    project_end_date = Column(Date, nullable=True)
    gantt_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ProjectRoadmap(project_id={self.project_id})>"
