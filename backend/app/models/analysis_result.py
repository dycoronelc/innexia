"""
Modelo analysis_results alineado con mysql/innexia.sql (result_json + columnas por módulo).
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    request_id = Column(
        String(100),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    result_json = Column(Text, nullable=False)
    executive_summary = Column(Text, nullable=True)
    market_analysis_json = Column(Text, nullable=True)
    bmc_json = Column(Text, nullable=True)
    strategy_json = Column(Text, nullable=True)
    financial_json = Column(Text, nullable=True)
    risks_json = Column(Text, nullable=True)
    roadmap_json = Column(Text, nullable=True)
    kanban_json = Column(Text, nullable=True)
    gantt_json = Column(Text, nullable=True)
    artifacts_json = Column(Text, nullable=True)
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    total_duration_seconds = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisResult(request_id={self.request_id})>"
