from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..core.auth import get_current_user
from ..models.user import User
from ..services.data_analysis_service import DataAnalysisService
from ..schemas.data_analysis import (
    UserAnalyticsResponse, RecommendationEngineResponse, 
    AnalyticsEventCreate, LearningPathResponse,
    UserInsights, LearningProgress, RecommendationQuery
)

router = APIRouter(tags=["Data Analysis"])


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working"""
    return {"message": "Data Analysis API is working", "status": "ok"}


@router.post("/track-event", response_model=dict)
async def track_analytics_event(
    event_data: AnalyticsEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track an analytics event"""
    try:
        analysis_service = DataAnalysisService(db)
        event = analysis_service.track_event(event_data)
        return {
            "success": True,
            "message": "Event tracked successfully",
            "data": {"event_id": event.id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking event: {str(e)}"
        )


@router.get("/analytics", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    try:
        analysis_service = DataAnalysisService(db)
        analytics = analysis_service.get_user_analytics(current_user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )


@router.post("/analytics/update", response_model=UserAnalyticsResponse)
async def update_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user analytics based on recent data"""
    try:
        analysis_service = DataAnalysisService(db)
        analytics = analysis_service.update_user_analytics(current_user.id)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating analytics: {str(e)}"
        )


@router.get("/insights", response_model=UserInsights)
async def get_user_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive user insights"""
    try:
        analysis_service = DataAnalysisService(db)
        insights = analysis_service.get_user_insights(current_user.id)
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating insights: {str(e)}"
        )


@router.get("/learning-progress", response_model=LearningProgress)
async def get_learning_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learning progress analysis"""
    try:
        analysis_service = DataAnalysisService(db)
        progress = analysis_service.get_learning_progress(current_user.id)
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving learning progress: {str(e)}"
        )


@router.post("/recommendations/generate", response_model=List[RecommendationEngineResponse])
async def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized recommendations"""
    try:
        analysis_service = DataAnalysisService(db)
        recommendations = analysis_service.generate_recommendations(current_user.id)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("/recommendations", response_model=List[RecommendationEngineResponse])
async def get_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user recommendations"""
    try:
        analysis_service = DataAnalysisService(db)
        recommendations = analysis_service.get_recommendations(current_user.id, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recommendations: {str(e)}"
        )


@router.put("/recommendations/{recommendation_id}/read", response_model=dict)
async def mark_recommendation_read(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as read"""
    try:
        analysis_service = DataAnalysisService(db)
        success = analysis_service.mark_recommendation_read(recommendation_id, current_user.id)
        if success:
            return {
                "success": True,
                "message": "Recommendation marked as read",
                "data": {"recommendation_id": recommendation_id}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking recommendation as read: {str(e)}"
        )


@router.put("/recommendations/{recommendation_id}/applied", response_model=dict)
async def mark_recommendation_applied(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recommendation as applied"""
    try:
        analysis_service = DataAnalysisService(db)
        success = analysis_service.mark_recommendation_applied(recommendation_id, current_user.id)
        if success:
            return {
                "success": True,
                "message": "Recommendation marked as applied",
                "data": {"recommendation_id": recommendation_id}
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking recommendation as applied: {str(e)}"
        )


@router.get("/dashboard", response_model=dict)
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard data"""
    try:
        # Return mock data for now to test the endpoint
        dashboard_data = {
            "analytics": {
                "login_frequency": 5.2,
                "session_duration": 25.5,
                "project_completion_rate": 75.0,
                "activity_completion_rate": 80.0,
                "content_consumption_rate": 60.0,
                "learning_progress": {"completed_courses": 3, "total_courses": 5},
                "preferred_content_types": ["video", "article"],
                "project_success_rate": 70.0,
                "business_model_complexity": 3.5,
                "market_research_depth": 4.0,
                "chatbot_usage_frequency": 2.5,
                "feature_usage_patterns": {"bmc": 8, "activities": 6, "documents": 4}
            },
            "insights": {
                "strengths": [
                    "Alto nivel de completitud en proyectos",
                    "Uso consistente de herramientas BMC",
                    "Buena frecuencia de sesiones",
                    "Aprovechamiento de contenido educativo"
                ],
                "improvement_areas": [
                    "Planificación financiera",
                    "Estrategia de marketing",
                    "Investigación de mercado",
                    "Uso del chatbot"
                ],
                "top_recommendations": [
                    {
                        "id": 1,
                        "type": "learning",
                        "title": "Complete your Business Model Canvas",
                        "description": "You have 2 incomplete BMC projects",
                        "priority": "high",
                        "category": "productivity"
                    },
                    {
                        "id": 2,
                        "type": "feature",
                        "title": "Try the guided interview feature",
                        "description": "Use our AI-powered interview to improve your business ideas",
                        "priority": "medium",
                        "category": "innovation"
                    }
                ],
                "learning_insights": {
                    "recommended_courses": ["Business Model Canvas", "Market Validation"],
                    "skill_gaps": ["Financial Planning", "Marketing Strategy"],
                    "learning_path": "Beginner to Intermediate"
                },
                "productivity_insights": {
                    "peak_usage_hours": "10:00-12:00",
                    "most_used_features": ["BMC", "Activities", "Documents"],
                    "completion_rate": 75.0
                }
            },
            "learning_progress": {
                "total_courses": 5,
                "completed_courses": 3,
                "in_progress_courses": 1,
                "completion_rate": 60.0,
                "overall_progress": 60.0,
                "current_learning_path": "Business Fundamentals",
                "next_recommended_course": "Advanced BMC Strategies",
                "next_recommendations": [
                    "Completar curso de Planificación Financiera",
                    "Tomar curso de Estrategias de Marketing",
                    "Aprender sobre Investigación de Mercado"
                ]
            },
            "top_recommendations": [
                {
                    "id": 1,
                    "recommendation_type": "learning",
                    "title": "Complete your Business Model Canvas",
                    "description": "You have 2 incomplete BMC projects that could benefit from completion",
                    "priority": 1,
                    "category": "productivity",
                    "is_read": False,
                    "is_applied": False,
                    "confidence_score": 0.85,
                    "metadata": {"project_count": 2}
                },
                {
                    "id": 2,
                    "recommendation_type": "feature",
                    "title": "Try the guided interview feature",
                    "description": "Use our AI-powered interview to improve your business ideas",
                    "priority": 2,
                    "category": "innovation",
                    "is_read": False,
                    "is_applied": False,
                    "confidence_score": 0.75,
                    "metadata": {"feature": "guided_interview"}
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )


@router.post("/track-login", response_model=dict)
async def track_user_login(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track user login event"""
    try:
        event_data = AnalyticsEventCreate(
            user_id=current_user.id,
            event_type="login",
            event_category="user_action",
            event_data={"timestamp": datetime.now().isoformat()},
            session_id=f"session_{current_user.id}_{datetime.now().timestamp()}"
        )
        
        analysis_service = DataAnalysisService(db)
        event = analysis_service.track_event(event_data)
        
        return {
            "success": True,
            "message": "Login event tracked successfully",
            "data": {"event_id": event.id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking login event: {str(e)}"
        )


@router.post("/track-content-view", response_model=dict)
async def track_content_view(
    content_id: int,
    content_type: str,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track content view event"""
    try:
        event_data = AnalyticsEventCreate(
            user_id=current_user.id,
            event_type="content_view",
            event_category="learning",
            event_data={
                "content_id": content_id,
                "content_type": content_type,
                "category": category,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        analysis_service = DataAnalysisService(db)
        event = analysis_service.track_event(event_data)
        
        return {
            "success": True,
            "message": "Content view event tracked successfully",
            "data": {"event_id": event.id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking content view event: {str(e)}"
        )


@router.post("/track-chatbot-interaction", response_model=dict)
async def track_chatbot_interaction(
    interaction_type: str,
    message_count: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track chatbot interaction event"""
    try:
        event_data = AnalyticsEventCreate(
            user_id=current_user.id,
            event_type="chatbot_interaction",
            event_category="interaction",
            event_data={
                "interaction_type": interaction_type,
                "message_count": message_count,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        analysis_service = DataAnalysisService(db)
        event = analysis_service.track_event(event_data)
        
        return {
            "success": True,
            "message": "Chatbot interaction event tracked successfully",
            "data": {"event_id": event.id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking chatbot interaction event: {str(e)}"
        )

