from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class BusinessModelCanvas(Base):
    __tablename__ = "business_model_canvases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, unique=True)
    
    # Elementos del Business Model Canvas
    key_partners = Column(Text, nullable=True)  # JSON como string
    key_activities = Column(Text, nullable=True)  # JSON como string
    key_resources = Column(Text, nullable=True)  # JSON como string
    value_propositions = Column(Text, nullable=True)  # JSON como string
    customer_relationships = Column(Text, nullable=True)  # JSON como string
    channels = Column(Text, nullable=True)  # JSON como string
    customer_segments = Column(Text, nullable=True)  # JSON como string
    cost_structure = Column(Text, nullable=True)  # JSON como string
    revenue_streams = Column(Text, nullable=True)  # JSON como string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    project = relationship("Project", back_populates="business_model_canvas")
    
    def __repr__(self):
        return f"<BusinessModelCanvas(id={self.id}, project_id={self.project_id})>"

