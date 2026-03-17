"""
Modelo analysis_requests alineado con mysql/innexia.sql (chat gateway + strategy engine).
"""
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from ..database import Base


class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(100), nullable=False, unique=True, index=True)
    project_id = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True)
    project_name = Column(String(255), nullable=True)
    organization_name = Column(String(255), nullable=True)
    analysis_type = Column(String(100), nullable=False, default="full_strategy")
    language_code = Column(String(10), nullable=False, default="es")
    input_message = Column(Text, nullable=False, server_default="")
    input_json = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="queued", index=True)
    progress = Column(Integer, nullable=False, default=0)
    current_stage = Column(String(100), nullable=True)
    callback_url = Column(String(500), nullable=True)
    callback_status = Column(String(50), nullable=True)
    callback_attempts = Column(Integer, nullable=False, default=0)
    callback_last_at = Column(DateTime(timezone=True), nullable=True)
    callback_response_code = Column(Integer, nullable=True)
    callback_response_body = Column(Text, nullable=True)
    workflow_version = Column(String(100), nullable=True)
    engine_version = Column(String(50), nullable=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisRequest(request_id={self.request_id}, project_id={self.project_id})>"
