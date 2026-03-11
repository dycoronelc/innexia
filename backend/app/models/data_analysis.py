from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class UserAnalytics(Base):
    __tablename__ = "user_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # User behavior metrics
    login_frequency = Column(Float, default=0.0)  # Average logins per week
    session_duration = Column(Float, default=0.0)  # Average session duration in minutes
    project_completion_rate = Column(Float, default=0.0)  # Percentage of completed projects
    activity_completion_rate = Column(Float, default=0.0)  # Percentage of completed activities
    
    # Learning metrics
    content_consumption_rate = Column(Float, default=0.0)  # Educational content consumed
    learning_progress = Column(JSON)  # Progress in different learning areas
    preferred_content_types = Column(JSON)  # Types of content user prefers
    
    # Business metrics
    project_success_rate = Column(Float, default=0.0)  # Success rate of projects
    business_model_complexity = Column(Float, default=0.0)  # Average complexity of BMCs
    market_research_depth = Column(Float, default=0.0)  # Depth of market research
    
    # Interaction patterns
    chatbot_usage_frequency = Column(Float, default=0.0)  # How often user uses chatbot
    feature_usage_patterns = Column(JSON)  # Which features are used most
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")


class RecommendationEngine(Base):
    __tablename__ = "recommendation_engine"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Recommendation types
    recommendation_type = Column(String(50), nullable=False)  # project, learning, content, activity
    category = Column(String(100))  # Specific category within type
    priority = Column(Integer, default=1)  # 1-5 priority scale
    
    # Recommendation content
    title = Column(String(200), nullable=False)
    description = Column(Text)
    reasoning = Column(Text)  # Why this recommendation was made
    expected_impact = Column(Float)  # Expected impact score (0-1)
    
    # Data sources used
    data_sources = Column(JSON)  # Which data sources were analyzed
    confidence_score = Column(Float, default=0.0)  # Confidence in recommendation
    
    # Action details
    action_url = Column(String(500))  # URL to take action
    action_type = Column(String(50))  # Type of action (navigate, create, learn, etc.)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_read = Column(Boolean, default=False)
    is_applied = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # When recommendation expires
    
    # Relationships
    user = relationship("User", back_populates="recommendations")


class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # project, activity, learning, interaction
    description = Column(Text)
    
    # Data collection settings
    collection_frequency = Column(String(50), default="daily")  # daily, weekly, monthly
    is_active = Column(Boolean, default=True)
    last_collection = Column(DateTime(timezone=True))
    
    # Data schema
    data_schema = Column(JSON)  # Schema of collected data
    collection_parameters = Column(JSON)  # Parameters for data collection
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(100), nullable=False)  # login, project_create, activity_complete, etc.
    event_category = Column(String(50))  # user_action, system_event, learning, business
    
    # Event data
    event_data = Column(JSON)  # Detailed event data
    metadata_info = Column(JSON)  # Additional metadata
    
    # Context
    session_id = Column(String(100))  # Session identifier
    project_id = Column(Integer, ForeignKey("projects.id"))
    activity_id = Column(Integer, ForeignKey("project_activities.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics_events")
    project = relationship("Project", overlaps="analytics_events")
    activity = relationship("ProjectActivity", overlaps="analytics_events")


class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Path details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # business, marketing, technical, etc.
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    
    # Progress tracking
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    
    # Content
    content_items = Column(JSON)  # Array of content items in the path
    prerequisites = Column(JSON)  # Prerequisites for this path
    
    # Status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")

