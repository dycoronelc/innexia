from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentMemoryBase(BaseModel):
    memory_type: str = Field(..., description="Tipo de memoria: conversation, context, preferences, state")
    key: str = Field(..., description="Clave de la memoria")
    value: Dict[str, Any] = Field(..., description="Valor de la memoria")
    importance: int = Field(default=1, ge=1, le=10, description="Importancia de la memoria (1-10)")
    expires_at: Optional[datetime] = Field(None, description="Fecha de expiración para memoria temporal")


class AgentMemoryCreate(AgentMemoryBase):
    session_id: str = Field(..., description="ID de la sesión")


class AgentMemoryUpdate(BaseModel):
    value: Optional[Dict[str, Any]] = None
    importance: Optional[int] = Field(None, ge=1, le=10)
    expires_at: Optional[datetime] = None


class AgentMemoryResponse(AgentMemoryBase):
    id: int
    user_id: int
    session_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationSessionBase(BaseModel):
    project_id: Optional[int] = Field(None, description="ID del proyecto asociado")
    current_context: Optional[Dict[str, Any]] = Field(None, description="Contexto actual de la conversación")
    conversation_summary: Optional[str] = Field(None, description="Resumen de la conversación")
    user_intent: Optional[str] = Field(None, description="Intención principal del usuario")


class ConversationSessionCreate(ConversationSessionBase):
    session_id: str = Field(..., description="ID único de la sesión")


class ConversationSessionUpdate(BaseModel):
    current_context: Optional[Dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    user_intent: Optional[str] = None
    is_active: Optional[bool] = None
    project_id: Optional[int] = None


class ConversationSessionResponse(ConversationSessionBase):
    id: int
    user_id: int
    session_id: str
    is_active: bool
    started_at: datetime
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConversationMessageBase(BaseModel):
    message_type: str = Field(..., description="Tipo de mensaje: user, agent, system")
    content: str = Field(..., description="Contenido del mensaje")
    metadata_info: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    intent_detected: Optional[str] = Field(None, description="Intención detectada")
    confidence_score: Optional[int] = Field(None, ge=0, le=100, description="Puntuación de confianza")


class ConversationMessageCreate(ConversationMessageBase):
    pass


class ConversationMessageResponse(ConversationMessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserContextBase(BaseModel):
    current_project_id: Optional[int] = Field(None, description="ID del proyecto actual")
    expertise_level: str = Field(default="beginner", description="Nivel de experiencia")
    business_sector: Optional[str] = Field(None, description="Sector de negocio")
    preferred_language: str = Field(default="es", description="Idioma preferido")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="Preferencias de notificación")
    learning_goals: Optional[Dict[str, Any]] = Field(None, description="Objetivos de aprendizaje")


class UserContextCreate(UserContextBase):
    pass


class UserContextUpdate(BaseModel):
    current_project_id: Optional[int] = None
    expertise_level: Optional[str] = None
    business_sector: Optional[str] = None
    preferred_language: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    learning_goals: Optional[Dict[str, Any]] = None


class UserContextResponse(UserContextBase):
    id: int
    user_id: int
    last_interaction: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemoryQuery(BaseModel):
    memory_type: Optional[str] = None
    key: Optional[str] = None
    session_id: Optional[str] = None
    importance_min: Optional[int] = Field(None, ge=1, le=10)
    include_expired: bool = Field(default=False, description="Incluir memorias expiradas")


class ConversationContext(BaseModel):
    session_id: str
    current_context: Dict[str, Any]
    recent_messages: List[ConversationMessageResponse]
    user_intent: Optional[str] = None
    conversation_summary: Optional[str] = None

