from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class ActivityAttachment(Base):
    __tablename__ = "activity_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("project_activities.id"), nullable=False)
    name = Column(String(200), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Ruta local del archivo
    file_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Tamaño en bytes
    description = Column(Text, nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    activity = relationship("ProjectActivity", back_populates="attachments")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<ActivityAttachment(id={self.id}, name='{self.name}', file_type='{self.file_type}')>"
