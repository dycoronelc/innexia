from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import validate_callback_token
from app.db.session import SessionLocal
from app.schemas.callback import CallbackAckResponse, StrategyCallbackRequest
from app.services.callback_service import CallbackService

router = APIRouter(prefix="/api/v1/callbacks", tags=["Callbacks"])



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/strategy",
    response_model=CallbackAckResponse,
    dependencies=[Depends(validate_callback_token)],
)
def strategy_callback(payload: StrategyCallbackRequest, db: Session = Depends(get_db)):
    service = CallbackService(db)
    service.process_strategy_callback(payload)

    return CallbackAckResponse(
        success=True,
        message="Callback procesado correctamente",
        request_id=payload.request_id,
    )
