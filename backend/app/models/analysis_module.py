"""
Traza de ejecución por módulo/agente del AI Strategy Engine.
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class AnalysisModule(Base):
    __tablename__ = "analysis_modules"
    __table_args__ = (
        UniqueConstraint("request_id", "module_name", name="uq_analysis_modules_request_module"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    request_id = Column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    module_name = Column(String(100), nullable=False)
    module_status = Column(
        Enum("pending", "running", "completed", "failed", name="analysis_module_status"),
        nullable=False,
        default="completed",
        index=True,
    )
    input_json = Column(Text, nullable=True)
    output_json = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisModule(request_id={self.request_id}, module_name={self.module_name})>"
