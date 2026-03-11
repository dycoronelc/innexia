import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from ..models.proactive_suggestions import (
    ProactiveSuggestion, 
    SuggestionRule, 
    UserSuggestionPreference
)
from ..models.project import Project
# from ..models.project_activity import ProjectActivity
from ..models.business_model_canvas import BusinessModelCanvas
from ..models.agent_memory import UserContext
from ..schemas.proactive_suggestions import (
    ProactiveSuggestionCreate,
    ProactiveSuggestionUpdate,
    SuggestionRuleCreate,
    SuggestionRuleUpdate,
    UserSuggestionPreferenceCreate,
    UserSuggestionPreferenceUpdate,
    SuggestionQuery,
    SuggestionInsight
)


class ProactiveSuggestionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_suggestion(self, user_id: int, suggestion_data: ProactiveSuggestionCreate) -> ProactiveSuggestion:
        """Crea una nueva sugerencia proactiva"""
        suggestion = ProactiveSuggestion(
            user_id=user_id,
            **suggestion_data.dict()
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)
        return suggestion
    
    def get_suggestions(self, user_id: int, query: SuggestionQuery) -> List[ProactiveSuggestion]:
        """Obtiene sugerencias según criterios de búsqueda"""
        db_query = self.db.query(ProactiveSuggestion).filter(ProactiveSuggestion.user_id == user_id)
        
        if query.suggestion_type:
            db_query = db_query.filter(ProactiveSuggestion.suggestion_type == query.suggestion_type)
        
        if query.category:
            db_query = db_query.filter(ProactiveSuggestion.category == query.category)
        
        if query.priority_min:
            db_query = db_query.filter(ProactiveSuggestion.priority >= query.priority_min)
        
        if query.is_read is not None:
            db_query = db_query.filter(ProactiveSuggestion.is_read == query.is_read)
        
        if query.is_dismissed is not None:
            db_query = db_query.filter(ProactiveSuggestion.is_dismissed == query.is_dismissed)
        
        return db_query.order_by(desc(ProactiveSuggestion.priority), desc(ProactiveSuggestion.created_at)).limit(query.limit).all()
    
    def mark_as_read(self, suggestion_id: int, user_id: int) -> Optional[ProactiveSuggestion]:
        """Marca una sugerencia como leída"""
        suggestion = self.db.query(ProactiveSuggestion).filter(
            and_(
                ProactiveSuggestion.id == suggestion_id,
                ProactiveSuggestion.user_id == user_id
            )
        ).first()
        
        if not suggestion:
            return None
        
        suggestion.is_read = True
        suggestion.read_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(suggestion)
        return suggestion
    
    def dismiss_suggestion(self, suggestion_id: int, user_id: int) -> Optional[ProactiveSuggestion]:
        """Descarta una sugerencia"""
        suggestion = self.db.query(ProactiveSuggestion).filter(
            and_(
                ProactiveSuggestion.id == suggestion_id,
                ProactiveSuggestion.user_id == user_id
            )
        ).first()
        
        if not suggestion:
            return None
        
        suggestion.is_dismissed = True
        suggestion.dismissed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(suggestion)
        return suggestion
    
    def get_or_create_user_preferences(self, user_id: int) -> UserSuggestionPreference:
        """Obtiene o crea las preferencias del usuario"""
        preferences = self.db.query(UserSuggestionPreference).filter(
            UserSuggestionPreference.user_id == user_id
        ).first()
        
        if not preferences:
            preferences = UserSuggestionPreference(user_id=user_id)
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
        
        return preferences
    
    def update_user_preferences(self, user_id: int, update_data: UserSuggestionPreferenceUpdate) -> UserSuggestionPreference:
        """Actualiza las preferencias del usuario"""
        preferences = self.get_or_create_user_preferences(user_id)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(preferences)
        return preferences
    
    def get_suggestion_insights(self, user_id: int) -> SuggestionInsight:
        """Obtiene insights sobre las sugerencias del usuario"""
        suggestions = self.db.query(ProactiveSuggestion).filter(
            ProactiveSuggestion.user_id == user_id
        ).all()
        
        total_suggestions = len(suggestions)
        unread_suggestions = len([s for s in suggestions if not s.is_read])
        high_priority_suggestions = len([s for s in suggestions if s.priority >= 7])
        
        suggestions_by_category = {}
        suggestions_by_type = {}
        total_priority = 0
        
        for suggestion in suggestions:
            # Por categoría
            category = suggestion.category or "general"
            suggestions_by_category[category] = suggestions_by_category.get(category, 0) + 1
            
            # Por tipo
            suggestions_by_type[suggestion.suggestion_type] = suggestions_by_type.get(suggestion.suggestion_type, 0) + 1
            
            total_priority += suggestion.priority
        
        average_priority = total_priority / total_suggestions if total_suggestions > 0 else 0
        
        return SuggestionInsight(
            total_suggestions=total_suggestions,
            unread_suggestions=unread_suggestions,
            high_priority_suggestions=high_priority_suggestions,
            suggestions_by_category=suggestions_by_category,
            suggestions_by_type=suggestions_by_type,
            average_priority=average_priority
        )
    
    def generate_project_suggestions(self, user_id: int) -> List[ProactiveSuggestion]:
        """Genera sugerencias basadas en el estado de los proyectos"""
        suggestions = []
        
        # Obtener proyectos del usuario
        projects = self.db.query(Project).filter(Project.owner_id == user_id).all()
        
        for project in projects:
            # Sugerencia para proyectos sin BMC
            bmc = self.db.query(BusinessModelCanvas).filter(
                BusinessModelCanvas.project_id == project.id
            ).first()
            
            if not bmc:
                suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                    suggestion_type="recommendation",
                    title="Generar Business Model Canvas",
                    description=f"Tu proyecto '{project.name}' aún no tiene un Business Model Canvas. Te sugiero generarlo para tener una visión clara de tu modelo de negocio.",
                    priority=8,
                    category="bmc",
                    action_url=f"/projects/{project.id}",
                    action_text="Generar BMC",
                    context_data={"project_id": project.id, "project_name": project.name}
                )))
            
            # Sugerencia para proyectos sin actividades
            activities = self.db.query(ProjectActivity).filter(
                ProjectActivity.project_id == project.id
            ).all()
            
            if not activities:
                suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                    suggestion_type="recommendation",
                    title="Crear actividades para el proyecto",
                    description=f"Tu proyecto '{project.name}' no tiene actividades definidas. Te sugiero crear un plan de acción con tareas específicas.",
                    priority=7,
                    category="activity",
                    action_url=f"/projects/{project.id}/activities",
                    action_text="Crear Actividades",
                    context_data={"project_id": project.id, "project_name": project.name}
                )))
            
            # Sugerencia para proyectos inactivos
            if project.status == "inactive" and (datetime.utcnow() - project.updated_at).days > 7:
                suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                    suggestion_type="reminder",
                    title="Proyecto inactivo",
                    description=f"Tu proyecto '{project.name}' lleva más de una semana sin actividad. ¿Te gustaría revisarlo o actualizar su estado?",
                    priority=6,
                    category="project",
                    action_url=f"/projects/{project.id}",
                    action_text="Revisar Proyecto",
                    context_data={"project_id": project.id, "project_name": project.name}
                )))
        
        return suggestions
    
    def generate_learning_suggestions(self, user_id: int) -> List[ProactiveSuggestion]:
        """Genera sugerencias de aprendizaje basadas en el contexto del usuario"""
        suggestions = []
        
        # Obtener contexto del usuario
        user_context = self.db.query(UserContext).filter(UserContext.user_id == user_id).first()
        
        if user_context:
            expertise_level = user_context.expertise_level
            business_sector = user_context.business_sector
            
            # Sugerencias basadas en nivel de experiencia
            if expertise_level == "beginner":
                suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                    suggestion_type="recommendation",
                    title="Aprende sobre Business Model Canvas",
                    description="Como emprendedor principiante, te recomiendo aprender sobre el Business Model Canvas para estructurar mejor tu idea de negocio.",
                    priority=6,
                    category="learning",
                    action_url="/learn",
                    action_text="Ir a Aprende",
                    context_data={"topic": "bmc", "level": "beginner"}
                )))
            
            # Sugerencias basadas en sector de negocio
            if business_sector:
                suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                    suggestion_type="opportunity",
                    title=f"Tendencias en {business_sector}",
                    description=f"Descubre las últimas tendencias y oportunidades en el sector {business_sector} para mantener tu proyecto actualizado.",
                    priority=5,
                    category="learning",
                    action_url="/learn",
                    action_text="Ver Tendencias",
                    context_data={"sector": business_sector}
                )))
        
        return suggestions
    
    def generate_time_based_suggestions(self, user_id: int) -> List[ProactiveSuggestion]:
        """Genera sugerencias basadas en el tiempo y patrones de uso"""
        suggestions = []
        
        # Obtener preferencias del usuario
        preferences = self.get_or_create_user_preferences(user_id)
        
        # Sugerencia de revisión semanal
        last_suggestion = self.db.query(ProactiveSuggestion).filter(
            and_(
                ProactiveSuggestion.user_id == user_id,
                ProactiveSuggestion.suggestion_type == "reminder",
                ProactiveSuggestion.category == "weekly_review"
            )
        ).order_by(desc(ProactiveSuggestion.created_at)).first()
        
        if not last_suggestion or (datetime.utcnow() - last_suggestion.created_at).days >= 7:
            suggestions.append(self.create_suggestion(user_id, ProactiveSuggestionCreate(
                suggestion_type="reminder",
                title="Revisión Semanal de Proyectos",
                description="Es momento de revisar el progreso de tus proyectos. Evalúa lo que has logrado y planifica las próximas acciones.",
                priority=5,
                category="weekly_review",
                action_url="/dashboard",
                action_text="Revisar Proyectos",
                context_data={"type": "weekly_review"}
            )))
        
        return suggestions
    
    def cleanup_expired_suggestions(self) -> int:
        """Limpia sugerencias expiradas"""
        expired_suggestions = self.db.query(ProactiveSuggestion).filter(
            and_(
                ProactiveSuggestion.expires_at.isnot(None),
                ProactiveSuggestion.expires_at <= datetime.utcnow()
            )
        ).all()
        
        count = len(expired_suggestions)
        for suggestion in expired_suggestions:
            self.db.delete(suggestion)
        
        self.db.commit()
        return count
