from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ProactiveSuggestionBase(BaseModel):
    suggestion_type: str = Field(..., description="Tipo de sugerencia: reminder, recommendation, alert, opportunity")
    title: str = Field(..., description="Título de la sugerencia")
    description: str = Field(..., description="Descripción detallada")
    priority: int = Field(default=1, ge=1, le=10, description="Prioridad de la sugerencia (1-10)")
    category: Optional[str] = Field(None, description="Categoría de la sugerencia")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Datos contextuales")
    action_url: Optional[str] = Field(None, description="URL para la acción sugerida")
    action_text: Optional[str] = Field(None, description="Texto del botón de acción")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración")


class ProactiveSuggestionCreate(ProactiveSuggestionBase):
    pass


class ProactiveSuggestionUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None


class ProactiveSuggestionResponse(ProactiveSuggestionBase):
    id: int
    user_id: int
    is_read: bool
    is_dismissed: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SuggestionRuleBase(BaseModel):
    rule_name: str = Field(..., description="Nombre único de la regla")
    rule_type: str = Field(..., description="Tipo de regla: schedule, condition, event")
    conditions: Dict[str, Any] = Field(..., description="Condiciones para activar la regla")
    suggestion_template: Dict[str, Any] = Field(..., description="Plantilla de la sugerencia")
    is_active: bool = Field(default=True, description="Si la regla está activa")
    priority: int = Field(default=5, ge=1, le=10, description="Prioridad de la regla")


class SuggestionRuleCreate(SuggestionRuleBase):
    pass


class SuggestionRuleUpdate(BaseModel):
    conditions: Optional[Dict[str, Any]] = None
    suggestion_template: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=10)


class SuggestionRuleResponse(SuggestionRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserSuggestionPreferenceBase(BaseModel):
    notification_frequency: str = Field(default="daily", description="Frecuencia de notificaciones")
    preferred_categories: Optional[List[str]] = Field(None, description="Categorías preferidas")
    max_suggestions_per_day: int = Field(default=10, ge=1, le=50, description="Máximo de sugerencias por día")
    quiet_hours_start: str = Field(default="22:00", description="Hora de inicio de silencio")
    quiet_hours_end: str = Field(default="08:00", description="Hora de fin de silencio")
    timezone: str = Field(default="UTC", description="Zona horaria del usuario")


class UserSuggestionPreferenceCreate(UserSuggestionPreferenceBase):
    pass


class UserSuggestionPreferenceUpdate(BaseModel):
    notification_frequency: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    max_suggestions_per_day: Optional[int] = Field(None, ge=1, le=50)
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None


class UserSuggestionPreferenceResponse(UserSuggestionPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SuggestionQuery(BaseModel):
    suggestion_type: Optional[str] = None
    category: Optional[str] = None
    priority_min: Optional[int] = Field(None, ge=1, le=10)
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    limit: int = Field(default=10, ge=1, le=50)


class SuggestionInsight(BaseModel):
    total_suggestions: int
    unread_suggestions: int
    high_priority_suggestions: int
    suggestions_by_category: Dict[str, int]
    suggestions_by_type: Dict[str, int]
    average_priority: float

