from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..core.auth import get_current_user
from ..models.user import User
from ..services.advanced_conversation_state_service import AdvancedConversationStateService
from ..schemas.conversation_state import (
    ConversationStateResponse, StateTransitionRequest, ContextUpdateRequest,
    MemoryUpdateRequest, ComplexConversationState
)

router = APIRouter(prefix="/conversation-state", tags=["Advanced Conversation State"])


@router.post("/state", response_model=ConversationStateResponse)
async def create_or_get_conversation_state(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or get conversation state for a session"""
    try:
        state_service = AdvancedConversationStateService(db)
        state = state_service.create_or_get_state(session_id, current_user.id)
        return state
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error managing conversation state: {str(e)}"
        )


@router.post("/transition", response_model=ConversationStateResponse)
async def transition_conversation_state(
    request: StateTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transition conversation state"""
    try:
        state_service = AdvancedConversationStateService(db)
        state = state_service.transition_state(request)
        return state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transitioning state: {str(e)}"
        )


@router.put("/context", response_model=ConversationStateResponse)
async def update_conversation_context(
    request: ContextUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation context"""
    try:
        state_service = AdvancedConversationStateService(db)
        state = state_service.update_context(request)
        return state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating context: {str(e)}"
        )


@router.put("/memory", response_model=ConversationStateResponse)
async def update_conversation_memory(
    request: MemoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation memory"""
    try:
        state_service = AdvancedConversationStateService(db)
        state = state_service.update_memory(request)
        return state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating memory: {str(e)}"
        )


@router.get("/complex-state/{session_id}", response_model=ComplexConversationState)
async def get_complex_conversation_state(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complex conversation state with all related data"""
    try:
        state_service = AdvancedConversationStateService(db)
        complex_state = state_service.get_complex_state(session_id, current_user.id)
        return complex_state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving complex state: {str(e)}"
        )


@router.post("/track-conversation-event", response_model=dict)
async def track_conversation_event(
    session_id: str,
    event_type: str,
    event_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track conversation event"""
    try:
        state_service = AdvancedConversationStateService(db)
        event = state_service.track_conversation_event(
            session_id=session_id,
            user_id=current_user.id,
            event_type=event_type,
            event_data=event_data
        )
        return {
            "success": True,
            "message": "Conversation event tracked successfully",
            "data": {"event_id": event.id}
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking conversation event: {str(e)}"
        )

