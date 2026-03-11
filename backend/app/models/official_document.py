from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class DocumentType(str, enum.Enum):
    GUIDE = "guide"
    MANUAL = "manual"
    BROCHURE = "brochure"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TEMPLATE = "template"
    FORM = "form"


class DocumentCategory(str, enum.Enum):
    HR = "hr"
    OPERATIONS = "operations"
    FINANCE = "finance"
    MARKETING = "marketing"
    SALES = "sales"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    TRAINING = "training"


class ApprovalStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class OfficialDocument(Base):
    __tablename__ = "official_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    document_type = Column(Enum(DocumentType), nullable=False)
    category = Column(Enum(DocumentCategory), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    version = Column(String(20), default="1.0")
    is_public = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=True)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.DRAFT)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    tags = Column(JSON)
    document_metadata = Column(JSON)  # Información adicional del documento
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relaciones
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
