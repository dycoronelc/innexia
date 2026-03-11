from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ConversationStateType(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TRANSITIONING = "transitioning"


class IntentType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CONTEXTUAL = "contextual"
    FALLBACK = "fallback"


# Conversation State Schemas
class ConversationStateBase(BaseModel):
    current_state: str
    state_type: ConversationStateType = ConversationStateType.ACTIVE
    state_data: Optional[Dict[str, Any]] = {}
    primary_context: Optional[str] = None
    secondary_contexts: Optional[List[str]] = []
    context_stack: Optional[List[Dict[str, Any]]] = []
    current_intent: Optional[str] = None
    intent_type: IntentType = IntentType.PRIMARY
    intent_confidence: float = 0.0
    intent_history: Optional[List[Dict[str, Any]]] = []
    flow_id: Optional[str] = None
    flow_step: int = 0
    flow_data: Optional[Dict[str, Any]] = {}
    flow_history: Optional[List[Dict[str, Any]]] = []
    short_term_memory: Optional[Dict[str, Any]] = {}
    long_term_memory: Optional[Dict[str, Any]] = {}
    memory_priority: Optional[Dict[str, int]] = {}
    active_threads: Optional[List[str]] = []
    thread_priorities: Optional[Dict[str, int]] = {}
    thread_contexts: Optional[Dict[str, Any]] = {}
    previous_state: Optional[str] = None
    transition_reason: Optional[str] = None
    transition_data: Optional[Dict[str, Any]] = {}


class ConversationStateCreate(ConversationStateBase):
    session_id: str
    user_id: int


class ConversationStateUpdate(BaseModel):
    current_state: Optional[str] = None
    state_type: Optional[ConversationStateType] = None
    state_data: Optional[Dict[str, Any]] = None
    primary_context: Optional[str] = None
    secondary_contexts: Optional[List[str]] = None
    context_stack: Optional[List[Dict[str, Any]]] = None
    current_intent: Optional[str] = None
    intent_type: Optional[IntentType] = None
    intent_confidence: Optional[float] = None
    intent_history: Optional[List[Dict[str, Any]]] = None
    flow_id: Optional[str] = None
    flow_step: Optional[int] = None
    flow_data: Optional[Dict[str, Any]] = None
    flow_history: Optional[List[Dict[str, Any]]] = None
    short_term_memory: Optional[Dict[str, Any]] = None
    long_term_memory: Optional[Dict[str, Any]] = None
    memory_priority: Optional[Dict[str, int]] = None
    active_threads: Optional[List[str]] = None
    thread_priorities: Optional[Dict[str, int]] = None
    thread_contexts: Optional[Dict[str, Any]] = None
    previous_state: Optional[str] = None
    transition_reason: Optional[str] = None
    transition_data: Optional[Dict[str, Any]] = None


class ConversationStateResponse(ConversationStateBase):
    id: int
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_activity: datetime
    
    class Config:
        from_attributes = True


# Advanced State Management Schemas
class StateTransitionRequest(BaseModel):
    session_id: str
    to_state: str
    transition_type: str = "automatic"
    transition_reason: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = {}
    intent_data: Optional[Dict[str, Any]] = {}


class ContextUpdateRequest(BaseModel):
    session_id: str
    primary_context: Optional[str] = None
    secondary_contexts: Optional[List[str]] = None
    context_stack: Optional[List[Dict[str, Any]]] = None


class IntentUpdateRequest(BaseModel):
    session_id: str
    current_intent: str
    intent_type: IntentType = IntentType.PRIMARY
    intent_confidence: float = 0.0
    intent_data: Optional[Dict[str, Any]] = {}


class ThreadManagementRequest(BaseModel):
    session_id: str
    thread_id: str
    action: str  # create, update, pause, resume, close
    thread_data: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None


class MemoryUpdateRequest(BaseModel):
    session_id: str
    memory_type: str  # short_term, long_term
    memory_key: str
    memory_value: Any
    priority: Optional[int] = None


class ComplexConversationState(BaseModel):
    session_id: str
    current_state: str
    contexts: Dict[str, Any]
    intents: List[Dict[str, Any]]
    flows: List[Dict[str, Any]]
    threads: List[Dict[str, Any]]
    memories: Dict[str, Any]
    last_activity: datetime

