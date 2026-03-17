"""
Actividades estructuradas generadas por el AI Strategy Engine para Kanban/Gantt.
"""
from sqlalchemy import Column, BigInteger, Integer, String, Text, Date, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class AnalysisActivity(Base):
    __tablename__ = "analysis_activities"
    __table_args__ = (
        UniqueConstraint("request_id", "activity_id", name="uq_analysis_activities_request_activity"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    request_id = Column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    activity_id = Column(String(50), nullable=False)
    epic = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(
        Enum("baja", "media", "alta", "critica", name="analysis_activity_priority"),
        nullable=True,
        default="media",
        index=True,
    )
    owner_role = Column(String(100), nullable=True)
    estimated_days = Column(Integer, nullable=True)
    depends_on_json = Column(Text, nullable=True)
    kanban_status = Column(
        Enum("todo", "in_progress", "review", "done", name="analysis_kanban_status"),
        nullable=False,
        default="todo",
        index=True,
    )
    phase_id = Column(String(50), nullable=True, index=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    sort_order = Column(Integer, nullable=True)
    raw_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisActivity(request_id={self.request_id}, activity_id={self.activity_id})>"
