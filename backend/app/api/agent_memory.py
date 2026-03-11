from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..core.auth import get_current_user
from ..models.user import User
from ..schemas.agent_memory import (
    AgentMemoryCreate,
    AgentMemoryUpdate,
    AgentMemoryResponse,
    ConversationSessionCreate,
    ConversationSessionUpdate,
    ConversationSessionResponse,
    ConversationMessageCreate,
    ConversationMessageResponse,
    UserContextCreate,
    UserContextUpdate,
    UserContextResponse,
    MemoryQuery,
    ConversationContext
)
from ..services.agent_memory_service import AgentMemoryService
from ..models.agent_memory import ConversationSession

router = APIRouter(prefix="/api/agent-memory", tags=["Agent Memory"])


@router.post("/sessions", response_model=ConversationSessionResponse)
async def create_session(
    session_data: ConversationSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva sesión de conversación"""
    memory_service = AgentMemoryService(db)
    session = memory_service.create_or_get_session(
        user_id=current_user.id,
        project_id=session_data.project_id
    )
    return session


@router.get("/sessions/current", response_model=ConversationSessionResponse)
async def get_current_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la sesión activa actual del usuario"""
    memory_service = AgentMemoryService(db)
    session = memory_service.create_or_get_session(user_id=current_user.id)
    return session


@router.put("/sessions/{session_id}", response_model=ConversationSessionResponse)
async def update_session(
    session_id: int,
    update_data: ConversationSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza una sesión de conversación"""
    memory_service = AgentMemoryService(db)
    session = memory_service.update_session_context(session_id, update_data.current_context or {})
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.post("/sessions/{session_id}/messages", response_model=ConversationMessageResponse)
async def add_message(
    session_id: int,
    message_data: ConversationMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añade un mensaje a la conversación"""
    memory_service = AgentMemoryService(db)
    message = memory_service.add_message(session_id, message_data)
    return message


@router.get("/sessions/{session_id}/messages", response_model=List[ConversationMessageResponse])
async def get_messages(
    session_id: int,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de mensajes de una sesión"""
    memory_service = AgentMemoryService(db)
    messages = memory_service.get_conversation_history(session_id, limit)
    return messages


@router.post("/memories", response_model=AgentMemoryResponse)
async def store_memory(
    memory_data: AgentMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Almacena una nueva memoria"""
    memory_service = AgentMemoryService(db)
    memory = memory_service.store_memory(
        user_id=current_user.id,
        session_id=memory_data.session_id,
        memory_type=memory_data.memory_type,
        key=memory_data.key,
        value=memory_data.value,
        importance=memory_data.importance,
        expires_at=memory_data.expires_at
    )
    return memory


@router.get("/memories", response_model=List[AgentMemoryResponse])
async def get_memories(
    memory_type: Optional[str] = Query(None),
    key: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    importance_min: Optional[int] = Query(None, ge=1, le=10),
    include_expired: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene memorias según criterios de búsqueda"""
    memory_service = AgentMemoryService(db)
    query = MemoryQuery(
        memory_type=memory_type,
        key=key,
        session_id=session_id,
        importance_min=importance_min,
        include_expired=include_expired
    )
    memories = memory_service.get_memories(current_user.id, query)
    return memories


@router.get("/memories/{memory_type}/{key}", response_model=AgentMemoryResponse)
async def get_memory(
    memory_type: str,
    key: str,
    session_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene una memoria específica"""
    memory_service = AgentMemoryService(db)
    memory = memory_service.get_memory(
        user_id=current_user.id,
        memory_type=memory_type,
        key=key,
        session_id=session_id
    )
    if not memory:
        raise HTTPException(status_code=404, detail="Memoria no encontrada")
    return memory


@router.put("/memories/{memory_id}", response_model=AgentMemoryResponse)
async def update_memory(
    memory_id: int,
    update_data: AgentMemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza una memoria existente"""
    memory_service = AgentMemoryService(db)
    memory = memory_service.update_memory(memory_id, update_data)
    if not memory:
        raise HTTPException(status_code=404, detail="Memoria no encontrada")
    return memory


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina una memoria"""
    memory_service = AgentMemoryService(db)
    success = memory_service.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memoria no encontrada")
    return {"message": "Memoria eliminada exitosamente"}


@router.get("/context", response_model=UserContextResponse)
async def get_user_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el contexto del usuario"""
    memory_service = AgentMemoryService(db)
    context = memory_service.get_or_create_user_context(current_user.id)
    return context


@router.put("/context", response_model=UserContextResponse)
async def update_user_context(
    update_data: UserContextUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza el contexto del usuario"""
    memory_service = AgentMemoryService(db)
    context = memory_service.update_user_context(current_user.id, update_data)
    return context


@router.get("/context/conversation/{session_id}", response_model=ConversationContext)
async def get_conversation_context(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el contexto completo de una conversación"""
    memory_service = AgentMemoryService(db)
    
    # Obtener sesión
    session = db.query(ConversationSession).filter(
        ConversationSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Obtener mensajes recientes
    messages = memory_service.get_conversation_history(session_id, limit=10)
    
    return ConversationContext(
        session_id=session.session_id,
        current_context=session.current_context or {},
        recent_messages=messages,
        user_intent=session.user_intent,
        conversation_summary=session.conversation_summary
    )


@router.post("/cleanup")
async def cleanup_expired_memories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Limpia memorias expiradas"""
    memory_service = AgentMemoryService(db)
    count = memory_service.cleanup_expired_memories()
    return {"message": f"Se eliminaron {count} memorias expiradas"}
