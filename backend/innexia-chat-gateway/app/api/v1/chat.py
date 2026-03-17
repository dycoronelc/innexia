from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.chat import (
    ChatResultResponse,
    ChatStatusResponse,
    ChatSubmitRequest,
    ChatSubmitResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/submit", response_model=ChatSubmitResponse)
async def submit_chat(payload: ChatSubmitRequest, db: Session = Depends(get_db)):
    service = ChatService(db)
    request_id = await service.submit_chat(payload)

    return ChatSubmitResponse(
        success=True,
        request_id=request_id,
        status="processing",
        message="Solicitud recibida y en proceso",
    )


@router.get("/status/{request_id}", response_model=ChatStatusResponse)
def get_status(request_id: str, db: Session = Depends(get_db)):
    service = ChatService(db)
    request = service.get_status(request_id)

    return ChatStatusResponse(
        success=True,
        request_id=request.request_id,
        status=request.status,
        progress=request.progress,
        current_stage=request.current_stage,
        error_code=request.error_code,
        error_message=request.error_message,
        created_at=request.created_at,
        updated_at=request.updated_at,
        completed_at=request.completed_at,
    )


@router.get("/result/{request_id}", response_model=ChatResultResponse)
def get_result(request_id: str, db: Session = Depends(get_db)):
    service = ChatService(db)
    request, result = service.get_result(request_id)

    return ChatResultResponse(
        success=True,
        request_id=request.request_id,
        status=request.status,
        result=result.result_json if result else None,
        executive_summary=result.executive_summary if result else None,
    )
