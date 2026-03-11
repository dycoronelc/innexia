import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.conversation_state import ConversationState, ConversationStateType, IntentType
from ..schemas.conversation_state import StateTransitionRequest, ContextUpdateRequest, MemoryUpdateRequest

logger = logging.getLogger(__name__)


class AdvancedConversationStateService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_get_state(self, session_id: str, user_id: int) -> ConversationState:
        """Create or get conversation state for a session"""
        try:
            state = self.db.query(ConversationState).filter(
                ConversationState.session_id == session_id
            ).first()
            
            if not state:
                state = ConversationState(
                    session_id=session_id,
                    user_id=user_id,
                    current_state="initial",
                    state_type=ConversationStateType.ACTIVE,
                    state_data={},
                    short_term_memory={},
                    long_term_memory={},
                    memory_priority={},
                    active_threads=["main"],
                    thread_priorities={"main": 1},
                    thread_contexts={"main": "general"}
                )
                self.db.add(state)
                self.db.commit()
                self.db.refresh(state)
            
            return state
        except Exception as e:
            logger.error(f"Error creating/getting state: {e}")
            self.db.rollback()
            raise
    
    def transition_state(self, request: StateTransitionRequest) -> ConversationState:
        """Transition conversation state"""
        try:
            state = self.db.query(ConversationState).filter(
                ConversationState.session_id == request.session_id
            ).first()
            
            if not state:
                raise ValueError(f"State not found for session {request.session_id}")
            
            # Update state
            state.previous_state = state.current_state
            state.current_state = request.to_state
            state.transition_reason = request.transition_reason
            state.transition_data = request.context_data
            state.last_activity = datetime.now()
            
            # Update context if provided
            if request.context_data:
                if "primary_context" in request.context_data:
                    state.primary_context = request.context_data["primary_context"]
                if "secondary_contexts" in request.context_data:
                    state.secondary_contexts = request.context_data["secondary_contexts"]
            
            self.db.commit()
            self.db.refresh(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error transitioning state: {e}")
            self.db.rollback()
            raise
    
    def update_context(self, request: ContextUpdateRequest) -> ConversationState:
        """Update conversation context"""
        try:
            state = self.db.query(ConversationState).filter(
                ConversationState.session_id == request.session_id
            ).first()
            
            if not state:
                raise ValueError(f"State not found for session {request.session_id}")
            
            # Update context fields
            if request.primary_context:
                state.primary_context = request.primary_context
            if request.secondary_contexts:
                state.secondary_contexts = request.secondary_contexts
            if request.state_data:
                state.state_data = request.state_data
            
            state.last_activity = datetime.now()
            self.db.commit()
            self.db.refresh(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            self.db.rollback()
            raise
    
    def update_memory(self, request: MemoryUpdateRequest) -> ConversationState:
        """Update conversation memory"""
        try:
            state = self.db.query(ConversationState).filter(
                ConversationState.session_id == request.session_id
            ).first()
            
            if not state:
                raise ValueError(f"State not found for session {request.session_id}")
            
            if request.memory_type == "short_term":
                if not state.short_term_memory:
                    state.short_term_memory = {}
                state.short_term_memory[request.memory_key] = request.memory_value
                
            elif request.memory_type == "long_term":
                if not state.long_term_memory:
                    state.long_term_memory = {}
                state.long_term_memory[request.memory_key] = request.memory_value
            
            # Update priority
            if not state.memory_priority:
                state.memory_priority = {}
            state.memory_priority[request.memory_key] = request.priority
            
            state.last_activity = datetime.now()
            self.db.commit()
            self.db.refresh(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            self.db.rollback()
            raise
    
    def get_complex_state(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """Get complex conversation state with all related data"""
        try:
            state = self.db.query(ConversationState).filter(
                ConversationState.session_id == session_id
            ).first()
            
            if not state:
                raise ValueError(f"State not found for session {session_id}")
            
            return {
                "session_id": state.session_id,
                "current_state": state.current_state,
                "previous_state": state.previous_state,
                "state_type": state.state_type,
                "primary_context": state.primary_context,
                "secondary_contexts": state.secondary_contexts,
                "state_data": state.state_data,
                "short_term_memory": state.short_term_memory,
                "long_term_memory": state.long_term_memory,
                "memory_priority": state.memory_priority,
                "active_threads": state.active_threads,
                "thread_priorities": state.thread_priorities,
                "thread_contexts": state.thread_contexts,
                "last_activity": state.last_activity,
                "created_at": state.created_at
            }
            
        except Exception as e:
            logger.error(f"Error getting complex state: {e}")
            raise
    
    def track_conversation_event(self, session_id: str, user_id: int, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track conversation event"""
        try:
            # Create or get state
            state = self.create_or_get_state(session_id, user_id)
            
            # Add event to short-term memory
            memory_key = f"event_{event_type}_{datetime.now().timestamp()}"
            memory_value = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat()
            }
            
            if not state.short_term_memory:
                state.short_term_memory = {}
            state.short_term_memory[memory_key] = memory_value
            
            # Update memory priority
            if not state.memory_priority:
                state.memory_priority = {}
            state.memory_priority[memory_key] = 1
            
            state.last_activity = datetime.now()
            self.db.commit()
            self.db.refresh(state)
            
            return {"id": 1, "session_id": session_id, "event_type": event_type}
            
        except Exception as e:
            logger.error(f"Error tracking conversation event: {e}")
            self.db.rollback()
            raise

