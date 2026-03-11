from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..core.auth import get_current_user
from ..models.user import User
from ..schemas.proactive_suggestions import (
    ProactiveSuggestionCreate,
    ProactiveSuggestionUpdate,
    ProactiveSuggestionResponse,
    SuggestionRuleCreate,
    SuggestionRuleUpdate,
    SuggestionRuleResponse,
    UserSuggestionPreferenceCreate,
    UserSuggestionPreferenceUpdate,
    UserSuggestionPreferenceResponse,
    SuggestionQuery,
    SuggestionInsight
)
from ..services.proactive_suggestion_service import ProactiveSuggestionService

router = APIRouter(prefix="/api/proactive-suggestions", tags=["Proactive Suggestions"])


@router.post("/", response_model=ProactiveSuggestionResponse)
async def create_suggestion(
    suggestion_data: ProactiveSuggestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva sugerencia proactiva"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestion = suggestion_service.create_suggestion(current_user.id, suggestion_data)
    return suggestion


@router.get("/", response_model=List[ProactiveSuggestionResponse])
async def get_suggestions(
    suggestion_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority_min: Optional[int] = Query(None, ge=1, le=10),
    is_read: Optional[bool] = Query(None),
    is_dismissed: Optional[bool] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene sugerencias según criterios de búsqueda"""
    suggestion_service = ProactiveSuggestionService(db)
    query = SuggestionQuery(
        suggestion_type=suggestion_type,
        category=category,
        priority_min=priority_min,
        is_read=is_read,
        is_dismissed=is_dismissed,
        limit=limit
    )
    suggestions = suggestion_service.get_suggestions(current_user.id, query)
    return suggestions


@router.get("/unread", response_model=List[ProactiveSuggestionResponse])
async def get_unread_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene sugerencias no leídas"""
    suggestion_service = ProactiveSuggestionService(db)
    query = SuggestionQuery(is_read=False, is_dismissed=False, limit=20)
    suggestions = suggestion_service.get_suggestions(current_user.id, query)
    return suggestions


@router.put("/{suggestion_id}/read", response_model=ProactiveSuggestionResponse)
async def mark_suggestion_as_read(
    suggestion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una sugerencia como leída"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestion = suggestion_service.mark_as_read(suggestion_id, current_user.id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
    return suggestion


@router.put("/{suggestion_id}/dismiss", response_model=ProactiveSuggestionResponse)
async def dismiss_suggestion(
    suggestion_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Descarta una sugerencia"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestion = suggestion_service.dismiss_suggestion(suggestion_id, current_user.id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Sugerencia no encontrada")
    return suggestion


@router.get("/insights", response_model=SuggestionInsight)
async def get_suggestion_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene insights sobre las sugerencias del usuario"""
    suggestion_service = ProactiveSuggestionService(db)
    insights = suggestion_service.get_suggestion_insights(current_user.id)
    return insights


@router.get("/preferences", response_model=UserSuggestionPreferenceResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene las preferencias de sugerencias del usuario"""
    suggestion_service = ProactiveSuggestionService(db)
    preferences = suggestion_service.get_or_create_user_preferences(current_user.id)
    return preferences


@router.put("/preferences", response_model=UserSuggestionPreferenceResponse)
async def update_user_preferences(
    update_data: UserSuggestionPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza las preferencias de sugerencias del usuario"""
    suggestion_service = ProactiveSuggestionService(db)
    preferences = suggestion_service.update_user_preferences(current_user.id, update_data)
    return preferences


@router.post("/generate/project", response_model=List[ProactiveSuggestionResponse])
async def generate_project_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera sugerencias basadas en el estado de los proyectos"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestions = suggestion_service.generate_project_suggestions(current_user.id)
    return suggestions


@router.post("/generate/learning", response_model=List[ProactiveSuggestionResponse])
async def generate_learning_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera sugerencias de aprendizaje basadas en el contexto del usuario"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestions = suggestion_service.generate_learning_suggestions(current_user.id)
    return suggestions


@router.post("/generate/time-based", response_model=List[ProactiveSuggestionResponse])
async def generate_time_based_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera sugerencias basadas en el tiempo y patrones de uso"""
    suggestion_service = ProactiveSuggestionService(db)
    suggestions = suggestion_service.generate_time_based_suggestions(current_user.id)
    return suggestions


@router.post("/generate/all", response_model=List[ProactiveSuggestionResponse])
async def generate_all_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera todas las sugerencias disponibles para el usuario"""
    suggestion_service = ProactiveSuggestionService(db)
    
    # Generar diferentes tipos de sugerencias
    project_suggestions = suggestion_service.generate_project_suggestions(current_user.id)
    learning_suggestions = suggestion_service.generate_learning_suggestions(current_user.id)
    time_based_suggestions = suggestion_service.generate_time_based_suggestions(current_user.id)
    
    # Combinar todas las sugerencias
    all_suggestions = project_suggestions + learning_suggestions + time_based_suggestions
    
    return all_suggestions


@router.post("/cleanup")
async def cleanup_expired_suggestions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Limpia sugerencias expiradas"""
    suggestion_service = ProactiveSuggestionService(db)
    count = suggestion_service.cleanup_expired_suggestions()
    return {"message": f"Se eliminaron {count} sugerencias expiradas"}

