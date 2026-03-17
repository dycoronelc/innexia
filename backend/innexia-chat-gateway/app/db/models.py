from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    project_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    project_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    analysis_type: Mapped[str] = mapped_column(String(100), nullable=False, default="full_strategy")
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="es")

    input_message: Mapped[str] = mapped_column(Text, nullable=False)
    input_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)

    callback_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    callback_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    callback_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    callback_response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    callback_response_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    workflow_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    market_analysis_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    bmc_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    strategy_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    financial_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risks_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    roadmap_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    kanban_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    gantt_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
