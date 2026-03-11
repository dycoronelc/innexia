from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Analytics Schemas
class UserAnalyticsBase(BaseModel):
    login_frequency: Optional[float] = 0.0
    session_duration: Optional[float] = 0.0
    project_completion_rate: Optional[float] = 0.0
    activity_completion_rate: Optional[float] = 0.0
    content_consumption_rate: Optional[float] = 0.0
    learning_progress: Optional[Dict[str, Any]] = {}
    preferred_content_types: Optional[List[str]] = []
    project_success_rate: Optional[float] = 0.0
    business_model_complexity: Optional[float] = 0.0
    market_research_depth: Optional[float] = 0.0
    chatbot_usage_frequency: Optional[float] = 0.0
    feature_usage_patterns: Optional[Dict[str, Any]] = {}


class UserAnalyticsCreate(UserAnalyticsBase):
    user_id: int


class UserAnalyticsUpdate(UserAnalyticsBase):
    pass


class UserAnalyticsResponse(UserAnalyticsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Recommendation Engine Schemas
class RecommendationEngineBase(BaseModel):
    recommendation_type: str = Field(..., description="Type of recommendation: project, learning, content, activity")
    category: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    title: str
    description: Optional[str] = None
    reasoning: Optional[str] = None
    expected_impact: Optional[float] = Field(None, ge=0.0, le=1.0)
    data_sources: Optional[List[str]] = []
    confidence_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0)
    action_url: Optional[str] = None
    action_type: Optional[str] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None


class RecommendationEngineCreate(RecommendationEngineBase):
    user_id: int


class RecommendationEngineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None
    is_read: Optional[bool] = None
    is_applied: Optional[bool] = None


class RecommendationEngineResponse(RecommendationEngineBase):
    id: int
    user_id: int
    is_read: bool
    is_applied: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Data Source Schemas
class DataSourceBase(BaseModel):
    name: str
    source_type: str = Field(..., description="Type of data source: project, activity, learning, interaction")
    description: Optional[str] = None
    collection_frequency: str = "daily"
    is_active: bool = True
    data_schema: Optional[Dict[str, Any]] = {}
    collection_parameters: Optional[Dict[str, Any]] = {}


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(DataSourceBase):
    name: Optional[str] = None
    source_type: Optional[str] = None
    collection_frequency: Optional[str] = None
    is_active: Optional[bool] = None


class DataSourceResponse(DataSourceBase):
    id: int
    last_collection: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analytics Event Schemas
class AnalyticsEventBase(BaseModel):
    event_type: str
    event_category: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = {}
    metadata_info: Optional[Dict[str, Any]] = {}
    session_id: Optional[str] = None
    project_id: Optional[int] = None
    activity_id: Optional[int] = None


class AnalyticsEventCreate(AnalyticsEventBase):
    user_id: int


class AnalyticsEventResponse(AnalyticsEventBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Learning Path Schemas
class LearningPathBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: str = Field(default="beginner", description="beginner, intermediate, advanced")
    current_step: int = 0
    total_steps: int = 0
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    content_items: Optional[List[Dict[str, Any]]] = []
    prerequisites: Optional[List[str]] = []
    is_active: bool = True


class LearningPathCreate(LearningPathBase):
    user_id: int


class LearningPathUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    current_step: Optional[int] = None
    completion_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class LearningPathResponse(LearningPathBase):
    id: int
    user_id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analysis Query Schemas
class AnalyticsQuery(BaseModel):
    user_id: int
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None


class RecommendationQuery(BaseModel):
    user_id: int
    recommendation_type: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True
    limit: int = Field(default=10, ge=1, le=50)


class LearningPathQuery(BaseModel):
    user_id: int
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_active: bool = True
    is_completed: Optional[bool] = None


# Analysis Result Schemas
class UserInsights(BaseModel):
    user_id: int
    behavior_patterns: Dict[str, Any]
    learning_preferences: Dict[str, Any]
    business_metrics: Dict[str, Any]
    improvement_areas: List[str]
    strengths: List[str]
    generated_at: datetime


class RecommendationInsight(BaseModel):
    recommendation_id: int
    user_id: int
    impact_prediction: float
    success_probability: float
    alternative_actions: List[str]
    generated_at: datetime


class LearningProgress(BaseModel):
    user_id: int
    overall_progress: float
    category_progress: Dict[str, float]
    next_recommendations: List[str]
    estimated_completion: Optional[datetime]
    generated_at: datetime

