import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from ..models.agent_memory import (
    AgentMemory, 
    ConversationSession, 
    ConversationMessage, 
    UserContext
)
from ..schemas.agent_memory import (
    AgentMemoryCreate,
    AgentMemoryUpdate,
    ConversationSessionCreate,
    ConversationSessionUpdate,
    ConversationMessageCreate,
    UserContextCreate,
    UserContextUpdate,
    MemoryQuery
)


class AgentMemoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_session_id(self) -> str:
        """Genera un ID único de sesión"""
        return str(uuid.uuid4())
    
    def create_or_get_session(self, user_id: int, project_id: Optional[int] = None) -> ConversationSession:
        """Crea una nueva sesión o recupera una existente activa"""
        # Buscar sesión activa existente
        existing_session = self.db.query(ConversationSession).filter(
            and_(
                ConversationSession.user_id == user_id,
                ConversationSession.status == "active"
            )
        ).first()
        
        if existing_session:
            # Actualizar proyecto si se proporciona uno nuevo
            if project_id and existing_session.project_id != project_id:
                existing_session.project_id = project_id
                self.db.commit()
            return existing_session
        
        # Crear nueva sesión
        session_id = self.generate_session_id()
        new_session = ConversationSession(
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            context_data={},
            status="active"
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session
    
    def store_memory(self, user_id: int, session_id: str, memory_type: str, key: str, 
                    value: Dict[str, Any], importance: int = 1, expires_at: Optional[datetime] = None) -> AgentMemory:
        """Almacena una nueva memoria"""
        memory = AgentMemory(
            user_id=user_id,
            session_id=session_id,
            memory_type=memory_type,
            key=key,
            value=value,
            importance=importance,
            expires_at=expires_at
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory
    
    def get_memory(self, user_id: int, memory_type: str, key: str, session_id: Optional[str] = None) -> Optional[AgentMemory]:
        """Recupera una memoria específica"""
        query = self.db.query(AgentMemory).filter(
            and_(
                AgentMemory.user_id == user_id,
                AgentMemory.memory_type == memory_type,
                AgentMemory.key == key,
                or_(
                    AgentMemory.expires_at.is_(None),
                    AgentMemory.expires_at > datetime.utcnow()
                )
            )
        )
        
        if session_id:
            query = query.filter(AgentMemory.session_id == session_id)
        
        return query.first()
    
    def get_memories(self, user_id: int, query: MemoryQuery) -> List[AgentMemory]:
        """Recupera memorias según criterios de búsqueda"""
        db_query = self.db.query(AgentMemory).filter(AgentMemory.user_id == user_id)
        
        if query.memory_type:
            db_query = db_query.filter(AgentMemory.memory_type == query.memory_type)
        
        if query.key:
            db_query = db_query.filter(AgentMemory.key == query.key)
        
        if query.session_id:
            db_query = db_query.filter(AgentMemory.session_id == query.session_id)
        
        if query.importance_min:
            db_query = db_query.filter(AgentMemory.importance >= query.importance_min)
        
        if not query.include_expired:
            db_query = db_query.filter(
                or_(
                    AgentMemory.expires_at.is_(None),
                    AgentMemory.expires_at > datetime.utcnow()
                )
            )
        
        return db_query.order_by(desc(AgentMemory.importance), desc(AgentMemory.created_at)).all()
    
    def update_memory(self, memory_id: int, update_data: AgentMemoryUpdate) -> Optional[AgentMemory]:
        """Actualiza una memoria existente"""
        memory = self.db.query(AgentMemory).filter(AgentMemory.id == memory_id).first()
        if not memory:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(memory, field, value)
        
        memory.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(memory)
        return memory
    
    def delete_memory(self, memory_id: int) -> bool:
        """Elimina una memoria"""
        memory = self.db.query(AgentMemory).filter(AgentMemory.id == memory_id).first()
        if not memory:
            return False
        
        self.db.delete(memory)
        self.db.commit()
        return True
    
    def add_message(self, session_id: int, message_data: ConversationMessageCreate) -> ConversationMessage:
        """Añade un mensaje a la conversación"""
        message = ConversationMessage(
            session_id=session_id,
            **message_data.dict()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_conversation_history(self, session_id: int, limit: int = 10) -> List[ConversationMessage]:
        """Obtiene el historial de conversación"""
        return self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(desc(ConversationMessage.created_at)).limit(limit).all()
    
    def update_session_context(self, session_id: int, context: Dict[str, Any]) -> ConversationSession:
        """Actualiza el contexto de la sesión"""
        session = self.db.query(ConversationSession).filter(ConversationSession.id == session_id).first()
        if not session:
            return None
        
        session.context_data = context
        session.last_activity = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_or_create_user_context(self, user_id: int) -> UserContext:
        """Obtiene o crea el contexto del usuario"""
        context = self.db.query(UserContext).filter(UserContext.user_id == user_id).first()
        if not context:
            context = UserContext(user_id=user_id)
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
        return context
    
    def update_user_context(self, user_id: int, update_data: UserContextUpdate) -> UserContext:
        """Actualiza el contexto del usuario"""
        context = self.get_or_create_user_context(user_id)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(context, field, value)
        
        context.last_interaction = datetime.utcnow()
        self.db.commit()
        self.db.refresh(context)
        return context
    
    def get_conversation_summary(self, session_id: int) -> str:
        """Genera un resumen de la conversación"""
        messages = self.get_conversation_history(session_id, limit=20)
        if not messages:
            return "Conversación vacía"
        
        # Crear resumen basado en los mensajes más importantes
        user_messages = [msg for msg in messages if msg.message_type == "user"]
        agent_messages = [msg for msg in messages if msg.message_type == "agent"]
        
        summary = f"Conversación con {len(user_messages)} mensajes del usuario y {len(agent_messages)} respuestas del agente."
        
        if user_messages:
            last_user_message = user_messages[0].content[:100] + "..." if len(user_messages[0].content) > 100 else user_messages[0].content
            summary += f" Último mensaje del usuario: {last_user_message}"
        
        return summary
    
    def cleanup_expired_memories(self) -> int:
        """Limpia memorias expiradas y retorna el número de memorias eliminadas"""
        expired_memories = self.db.query(AgentMemory).filter(
            and_(
                AgentMemory.expires_at.isnot(None),
                AgentMemory.expires_at <= datetime.utcnow()
            )
        ).all()
        
        count = len(expired_memories)
        for memory in expired_memories:
            self.db.delete(memory)
        
        self.db.commit()
        return count

