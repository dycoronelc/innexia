from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ConversationStateType(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TRANSITIONING = "transitioning"


class IntentType(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CONTEXTUAL = "contextual"
    FALLBACK = "fallback"


class ConversationState(Base):
    __tablename__ = "conversation_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # State information
    current_state = Column(String(100), nullable=False)  # Current conversation state
    state_type = Column(Enum(ConversationStateType), default=ConversationStateType.ACTIVE)
    state_data = Column(JSON)  # Current state data
    
    # Context management
    primary_context = Column(String(100))  # Main conversation context
    secondary_contexts = Column(JSON)  # Additional contexts
    context_stack = Column(JSON)  # Stack of contexts for nested conversations
    
    # Intent management
    current_intent = Column(String(100))  # Current primary intent
    intent_type = Column(Enum(IntentType), default=IntentType.PRIMARY)
    intent_confidence = Column(Float, default=0.0)
    intent_history = Column(JSON)  # History of intents in this session
    
    # Flow management
    flow_id = Column(String(100))  # Current conversation flow
    flow_step = Column(Integer, default=0)  # Current step in the flow
    flow_data = Column(JSON)  # Data specific to current flow
    flow_history = Column(JSON)  # History of flow transitions
    
    # Temporal context
    short_term_memory = Column(JSON)  # Recent conversation elements
    long_term_memory = Column(JSON)  # Persistent conversation elements
    memory_priority = Column(JSON)  # Priority levels for different memories
    
    # Parallel conversations
    active_threads = Column(JSON)  # Multiple conversation threads
    thread_priorities = Column(JSON)  # Priority for each thread
    thread_contexts = Column(JSON)  # Context for each thread
    
    # State transitions
    previous_state = Column(String(100))
    transition_reason = Column(String(200))
    transition_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversation_states", overlaps="conversation_states")


class ConversationFlow(Base):
    __tablename__ = "conversation_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Flow structure
    flow_type = Column(String(50))  # linear, branching, dynamic, adaptive
    flow_steps = Column(JSON)  # Steps in the flow
    flow_rules = Column(JSON)  # Rules for flow transitions
    flow_conditions = Column(JSON)  # Conditions for different paths
    
    # Flow management
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    priority = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StateTransition(Base):
    __tablename__ = "state_transitions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    
    # Transition details
    from_state = Column(String(100), nullable=False)
    to_state = Column(String(100), nullable=False)
    transition_type = Column(String(50))  # automatic, user_triggered, system_triggered
    transition_reason = Column(String(200))
    
    # Context at transition
    context_data = Column(JSON)
    intent_data = Column(JSON)
    flow_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConversationThread(Base):
    __tablename__ = "conversation_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    thread_id = Column(String(100), nullable=False)
    
    # Thread information
    thread_type = Column(String(50))  # main, background, parallel, nested
    thread_context = Column(String(100))
    thread_data = Column(JSON)
    
    # Thread state
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Thread relationships
    parent_thread_id = Column(String(100))  # For nested threads
    related_threads = Column(JSON)  # Related thread IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

