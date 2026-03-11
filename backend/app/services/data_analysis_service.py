import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json
import statistics

from ..models.data_analysis import (
    UserAnalytics, RecommendationEngine, DataSource, 
    AnalyticsEvent, LearningPath
)
from ..models.project import Project
from ..models.activity import ProjectActivity
from ..models.business_model_canvas import BusinessModelCanvas
from ..models.educational_content import EducationalContent
from ..schemas.data_analysis import (
    UserAnalyticsCreate, UserAnalyticsUpdate,
    RecommendationEngineCreate, RecommendationEngineUpdate,
    AnalyticsEventCreate, LearningPathCreate, LearningPathUpdate,
    UserInsights, RecommendationInsight, LearningProgress
)

logger = logging.getLogger(__name__)


class DataAnalysisService:
    def __init__(self, db: Session):
        self.db = db
    
    def track_event(self, event_data: AnalyticsEventCreate) -> AnalyticsEvent:
        """Track an analytics event"""
        try:
            event = AnalyticsEvent(**event_data.dict())
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            self.db.rollback()
            raise
    
    def get_user_analytics(self, user_id: int) -> Optional[UserAnalytics]:
        """Get or create user analytics"""
        analytics = self.db.query(UserAnalytics).filter(UserAnalytics.user_id == user_id).first()
        if not analytics:
            analytics = UserAnalytics(user_id=user_id)
            self.db.add(analytics)
            self.db.commit()
            self.db.refresh(analytics)
        return analytics
    
    def update_user_analytics(self, user_id: int) -> UserAnalytics:
        """Update user analytics based on recent data"""
        try:
            analytics = self.get_user_analytics(user_id)
            
            # Calculate login frequency (logins per week)
            week_ago = datetime.now() - timedelta(days=7)
            login_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type == "login",
                    AnalyticsEvent.created_at >= week_ago
                )
            ).count()
            analytics.login_frequency = login_events / 7.0
            
            # Calculate session duration
            session_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type == "session_end",
                    AnalyticsEvent.created_at >= week_ago
                )
            ).all()
            
            if session_events:
                durations = []
                for event in session_events:
                    if event.event_data and "duration" in event.event_data:
                        durations.append(event.event_data["duration"])
                if durations:
                    analytics.session_duration = statistics.mean(durations)
            
            # Calculate project completion rate
            total_projects = self.db.query(Project).filter(Project.user_id == user_id).count()
            completed_projects = self.db.query(Project).filter(
                and_(
                    Project.user_id == user_id,
                    Project.status == "completed"
                )
            ).count()
            analytics.project_completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
            
            # Calculate activity completion rate
            total_activities = self.db.query(ProjectActivity).join(Project).filter(Project.user_id == user_id).count()
            completed_activities = self.db.query(ProjectActivity).join(Project).filter(
                and_(
                    Project.user_id == user_id,
                    ProjectActivity.status == "completed"
                )
            ).count()
            analytics.activity_completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            
            # Calculate content consumption rate
            content_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type.in_(["content_view", "content_complete"]),
                    AnalyticsEvent.created_at >= week_ago
                )
            ).count()
            analytics.content_consumption_rate = content_events / 7.0
            
            # Analyze learning progress
            learning_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_category == "learning",
                    AnalyticsEvent.created_at >= week_ago
                )
            ).all()
            
            learning_progress = {}
            for event in learning_events:
                if event.event_data and "category" in event.event_data:
                    category = event.event_data["category"]
                    if category not in learning_progress:
                        learning_progress[category] = {"views": 0, "completions": 0}
                    if event.event_type == "content_view":
                        learning_progress[category]["views"] += 1
                    elif event.event_type == "content_complete":
                        learning_progress[category]["completions"] += 1
            
            analytics.learning_progress = learning_progress
            
            # Analyze preferred content types
            content_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type == "content_view",
                    AnalyticsEvent.created_at >= week_ago
                )
            ).all()
            
            content_types = {}
            for event in content_events:
                if event.event_data and "content_type" in event.event_data:
                    content_type = event.event_data["content_type"]
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            # Get top 3 preferred content types
            preferred_types = sorted(content_types.items(), key=lambda x: x[1], reverse=True)[:3]
            analytics.preferred_content_types = [content_type for content_type, _ in preferred_types]
            
            # Calculate business metrics
            projects = self.db.query(Project).filter(Project.user_id == user_id).all()
            if projects:
                # Project success rate (projects with completed activities)
                successful_projects = 0
                total_complexity = 0
                total_research_depth = 0
                
                for project in projects:
                    activities = self.db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).all()
                    if activities:
                        completed_activities = [a for a in activities if a.status == "completed"]
                        if len(completed_activities) > 0:
                            successful_projects += 1
                    
                    # Analyze BMC complexity
                    bmc = self.db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project.id).first()
                    if bmc:
                        complexity_score = 0
                        if bmc.key_partners and len(bmc.key_partners) > 0:
                            complexity_score += 1
                        if bmc.key_activities and len(bmc.key_activities) > 0:
                            complexity_score += 1
                        if bmc.value_propositions and len(bmc.value_propositions) > 0:
                            complexity_score += 1
                        if bmc.customer_relationships and len(bmc.customer_relationships) > 0:
                            complexity_score += 1
                        if bmc.channels and len(bmc.channels) > 0:
                            complexity_score += 1
                        if bmc.key_resources and len(bmc.key_resources) > 0:
                            complexity_score += 1
                        if bmc.cost_structure and len(bmc.cost_structure) > 0:
                            complexity_score += 1
                        if bmc.revenue_streams and len(bmc.revenue_streams) > 0:
                            complexity_score += 1
                        
                        total_complexity += complexity_score / 9.0  # Normalize to 0-1
                
                analytics.project_success_rate = (successful_projects / len(projects) * 100) if projects else 0
                analytics.business_model_complexity = total_complexity / len(projects) if projects else 0
            
            # Calculate chatbot usage frequency
            chatbot_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type == "chatbot_interaction",
                    AnalyticsEvent.created_at >= week_ago
                )
            ).count()
            analytics.chatbot_usage_frequency = chatbot_events / 7.0
            
            # Analyze feature usage patterns
            feature_events = self.db.query(AnalyticsEvent).filter(
                and_(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.created_at >= week_ago
                )
            ).all()
            
            feature_usage = {}
            for event in feature_events:
                feature = event.event_type
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
            
            analytics.feature_usage_patterns = feature_usage
            
            self.db.commit()
            self.db.refresh(analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Error updating user analytics: {e}")
            self.db.rollback()
            raise
    
    def generate_recommendations(self, user_id: int) -> List[RecommendationEngine]:
        """Generate personalized recommendations based on user analytics"""
        try:
            analytics = self.get_user_analytics(user_id)
            recommendations = []
            
            # Project-based recommendations
            if analytics.project_completion_rate < 50:
                recommendations.append(RecommendationEngine(
                    user_id=user_id,
                    recommendation_type="project",
                    category="completion",
                    priority=3,
                    title="Mejora tu tasa de finalización de proyectos",
                    description="Tu tasa de finalización de proyectos es del {:.1f}%. Te recomendamos enfocarte en completar proyectos existentes antes de crear nuevos.",
                    reasoning="Basado en tu baja tasa de finalización de proyectos",
                    expected_impact=0.7,
                    data_sources=["project_completion_rate"],
                    confidence_score=0.8,
                    action_url="/projects",
                    action_type="navigate"
                ))
            
            # Learning recommendations
            if analytics.content_consumption_rate < 2:
                recommendations.append(RecommendationEngine(
                    user_id=user_id,
                    recommendation_type="learning",
                    category="content_consumption",
                    priority=2,
                    title="Aumenta tu consumo de contenido educativo",
                    description="Consumes poco contenido educativo. Te recomendamos revisar la sección 'Aprende' para mejorar tus habilidades empresariales.",
                    reasoning="Basado en tu bajo consumo de contenido educativo",
                    expected_impact=0.6,
                    data_sources=["content_consumption_rate"],
                    confidence_score=0.7,
                    action_url="/learn",
                    action_type="navigate"
                ))
            
            # Business model recommendations
            if analytics.business_model_complexity < 0.5:
                recommendations.append(RecommendationEngine(
                    user_id=user_id,
                    recommendation_type="project",
                    category="business_model",
                    priority=4,
                    title="Desarrolla modelos de negocio más completos",
                    description="Tus modelos de negocio podrían ser más detallados. Usa el chatbot para generar un BMC más completo.",
                    reasoning="Basado en la complejidad de tus modelos de negocio",
                    expected_impact=0.8,
                    data_sources=["business_model_complexity"],
                    confidence_score=0.9,
                    action_url="/chatbot",
                    action_type="navigate"
                ))
            
            # Activity recommendations
            if analytics.activity_completion_rate < 60:
                recommendations.append(RecommendationEngine(
                    user_id=user_id,
                    recommendation_type="activity",
                    category="completion",
                    priority=3,
                    title="Completa más actividades",
                    description="Tu tasa de finalización de actividades es del {:.1f}%. Organiza mejor tu tiempo para completar las tareas pendientes.",
                    reasoning="Basado en tu baja tasa de finalización de actividades",
                    expected_impact=0.6,
                    data_sources=["activity_completion_rate"],
                    confidence_score=0.7,
                    action_url="/activities",
                    action_type="navigate"
                ))
            
            # Chatbot usage recommendations
            if analytics.chatbot_usage_frequency < 1:
                recommendations.append(RecommendationEngine(
                    user_id=user_id,
                    recommendation_type="interaction",
                    category="chatbot",
                    priority=2,
                    title="Usa más el chatbot inteligente",
                    description="El chatbot puede ayudarte a generar documentos, mejorar tu BMC y crear actividades más específicas.",
                    reasoning="Basado en tu bajo uso del chatbot",
                    expected_impact=0.5,
                    data_sources=["chatbot_usage_frequency"],
                    confidence_score=0.6,
                    action_url="/chatbot",
                    action_type="navigate"
                ))
            
            # Save recommendations
            for rec in recommendations:
                self.db.add(rec)
            
            self.db.commit()
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            self.db.rollback()
            raise
    
    def get_user_insights(self, user_id: int) -> UserInsights:
        """Generate comprehensive user insights"""
        try:
            analytics = self.get_user_analytics(user_id)
            
            # Behavior patterns
            behavior_patterns = {
                "login_frequency": analytics.login_frequency,
                "session_duration": analytics.session_duration,
                "feature_usage": analytics.feature_usage_patterns,
                "chatbot_usage": analytics.chatbot_usage_frequency
            }
            
            # Learning preferences
            learning_preferences = {
                "content_consumption": analytics.content_consumption_rate,
                "preferred_types": analytics.preferred_content_types,
                "learning_progress": analytics.learning_progress
            }
            
            # Business metrics
            business_metrics = {
                "project_completion": analytics.project_completion_rate,
                "activity_completion": analytics.activity_completion_rate,
                "project_success": analytics.project_success_rate,
                "bmc_complexity": analytics.business_model_complexity,
                "market_research": analytics.market_research_depth
            }
            
            # Identify improvement areas
            improvement_areas = []
            if analytics.project_completion_rate < 50:
                improvement_areas.append("Finalización de proyectos")
            if analytics.activity_completion_rate < 60:
                improvement_areas.append("Gestión de actividades")
            if analytics.content_consumption_rate < 2:
                improvement_areas.append("Consumo de contenido educativo")
            if analytics.business_model_complexity < 0.5:
                improvement_areas.append("Desarrollo de modelos de negocio")
            
            # Identify strengths
            strengths = []
            if analytics.project_completion_rate > 70:
                strengths.append("Alta tasa de finalización de proyectos")
            if analytics.content_consumption_rate > 3:
                strengths.append("Alto consumo de contenido educativo")
            if analytics.business_model_complexity > 0.7:
                strengths.append("Modelos de negocio bien desarrollados")
            if analytics.chatbot_usage_frequency > 2:
                strengths.append("Uso activo del chatbot")
            
            return UserInsights(
                user_id=user_id,
                behavior_patterns=behavior_patterns,
                learning_preferences=learning_preferences,
                business_metrics=business_metrics,
                improvement_areas=improvement_areas,
                strengths=strengths,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating user insights: {e}")
            raise
    
    def get_learning_progress(self, user_id: int) -> LearningProgress:
        """Generate learning progress analysis"""
        try:
            analytics = self.get_user_analytics(user_id)
            
            # Calculate overall progress
            overall_progress = min(100, (
                analytics.content_consumption_rate * 10 +
                len(analytics.learning_progress) * 20 +
                analytics.project_completion_rate * 0.3
            ))
            
            # Category progress
            category_progress = {}
            for category, data in analytics.learning_progress.items():
                if data["views"] > 0:
                    completion_rate = (data["completions"] / data["views"]) * 100
                    category_progress[category] = min(100, completion_rate)
            
            # Next recommendations
            next_recommendations = []
            if analytics.content_consumption_rate < 2:
                next_recommendations.append("Consumir más contenido educativo")
            if len(analytics.learning_progress) < 3:
                next_recommendations.append("Explorar nuevas categorías de aprendizaje")
            if analytics.project_completion_rate < 50:
                next_recommendations.append("Completar proyectos pendientes")
            
            # Estimate completion time
            estimated_completion = None
            if overall_progress < 100:
                # Rough estimation based on current progress
                weeks_to_complete = max(1, int((100 - overall_progress) / 10))
                estimated_completion = datetime.now() + timedelta(weeks=weeks_to_complete)
            
            return LearningProgress(
                user_id=user_id,
                overall_progress=overall_progress,
                category_progress=category_progress,
                next_recommendations=next_recommendations,
                estimated_completion=estimated_completion,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating learning progress: {e}")
            raise
    
    def get_recommendations(self, user_id: int, limit: int = 10) -> List[RecommendationEngine]:
        """Get user recommendations"""
        return self.db.query(RecommendationEngine).filter(
            and_(
                RecommendationEngine.user_id == user_id,
                RecommendationEngine.is_active == True
            )
        ).order_by(RecommendationEngine.priority.desc(), RecommendationEngine.created_at.desc()).limit(limit).all()
    
    def mark_recommendation_read(self, recommendation_id: int, user_id: int) -> bool:
        """Mark a recommendation as read"""
        try:
            recommendation = self.db.query(RecommendationEngine).filter(
                and_(
                    RecommendationEngine.id == recommendation_id,
                    RecommendationEngine.user_id == user_id
                )
            ).first()
            
            if recommendation:
                recommendation.is_read = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking recommendation as read: {e}")
            self.db.rollback()
            return False
    
    def mark_recommendation_applied(self, recommendation_id: int, user_id: int) -> bool:
        """Mark a recommendation as applied"""
        try:
            recommendation = self.db.query(RecommendationEngine).filter(
                and_(
                    RecommendationEngine.id == recommendation_id,
                    RecommendationEngine.user_id == user_id
                )
            ).first()
            
            if recommendation:
                recommendation.is_applied = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking recommendation as applied: {e}")
            self.db.rollback()
            return False

