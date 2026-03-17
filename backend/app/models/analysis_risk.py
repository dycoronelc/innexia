"""
Riesgos estructurados generados por el AI Strategy Engine.
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.sql import func

from ..database import Base


class AnalysisRisk(Base):
    __tablename__ = "analysis_risks"
    __table_args__ = (
        UniqueConstraint("request_id", "risk_id", name="uq_analysis_risks_request_risk"),
    )

    id = Column(BigInteger, primary_key=True, index=True)
    request_id = Column(
        String(64),
        ForeignKey("analysis_requests.request_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    risk_id = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    probability = Column(
        Enum("baja", "media", "alta", name="analysis_risk_probability"),
        nullable=True,
        default="media",
        index=True,
    )
    impact = Column(
        Enum("bajo", "medio", "alto", "critico", name="analysis_risk_impact"),
        nullable=True,
        default="medio",
        index=True,
    )
    mitigation = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    raw_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AnalysisRisk(request_id={self.request_id}, risk_id={self.risk_id})>"
