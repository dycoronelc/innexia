from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    project_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    project_name: Mapped[str] = mapped_column(String(255), index=True)
    analysis_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="es")
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    input_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "completed", "failed", name="analysis_request_status"),
        default="pending",
        index=True,
    )
    workflow_version: Mapped[str] = mapped_column(String(20))
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        index=True,
    )
    consolidated_json: Mapped[str] = mapped_column(Text)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    verdict_decision: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    market_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    viability_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AnalysisModule(Base):
    __tablename__ = "analysis_modules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    module_name: Mapped[str] = mapped_column(String(100))
    module_status: Mapped[str] = mapped_column(
        Enum("pending", "running", "completed", "failed", name="analysis_module_status"),
        default="completed",
    )
    input_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[str | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AnalysisActivity(Base):
    __tablename__ = "analysis_activities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    activity_id: Mapped[str] = mapped_column(String(50))
    epic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str | None] = mapped_column(
        Enum("baja", "media", "alta", "critica", name="analysis_activity_priority"),
        default="media",
        nullable=True,
    )
    owner_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    depends_on_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    kanban_status: Mapped[str] = mapped_column(
        Enum("todo", "in_progress", "review", "done", name="analysis_kanban_status"),
        default="todo",
        index=True,
    )
    phase_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    start_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AnalysisRisk(Base):
    __tablename__ = "analysis_risks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    risk_id: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    probability: Mapped[str | None] = mapped_column(
        Enum("baja", "media", "alta", name="analysis_risk_probability"),
        default="media",
        nullable=True,
    )
    impact: Mapped[str | None] = mapped_column(
        Enum("bajo", "medio", "alto", "critico", name="analysis_risk_impact"),
        default="medio",
        nullable=True,
    )
    mitigation: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
