"""
Modelo para almacenar documentos de proyectos y documentos generados por el sistema
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class ProjectDocument(Base):
    """Modelo para documentos subidos por usuarios a proyectos"""
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="documents")
    uploader = relationship("User", back_populates="documents")
    
    def __repr__(self):
        return f"<ProjectDocument(id={self.id}, filename='{self.filename}', project_id={self.project_id})>"

class GeneratedDocument(Base):
    """Modelo para documentos generados por el sistema"""
    __tablename__ = "generated_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # business_plan, marketing_plan, etc.
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    is_downloaded = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)
    metadata_info = Column(JSON, nullable=True)  # Información adicional del documento (renombrado de metadata)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", overlaps="generated_documents")
    user = relationship("User", overlaps="generated_documents")
    
    def __repr__(self):
        return f"<GeneratedDocument(id={self.id}, type={self.document_type}, title='{self.title}')>"

class DocumentTemplate(Base):
    """Modelo para plantillas de documentos"""
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    document_type = Column(String(50), nullable=False)
    template_content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Variables que se pueden reemplazar
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}', type={self.document_type})>"

class DocumentGenerationLog(Base):
    """Modelo para registrar logs de generación de documentos"""
    __tablename__ = "document_generation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, error, pending
    error_message = Column(Text, nullable=True)
    generation_time = Column(Integer, nullable=True)  # Tiempo en segundos
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    project = relationship("Project", overlaps="document_logs")
    user = relationship("User", overlaps="document_generation_logs")
    
    def __repr__(self):
        return f"<DocumentGenerationLog(id={self.id}, type={self.document_type}, status={self.status})>"