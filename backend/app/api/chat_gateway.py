"""
Routers del chat gateway (compatible con innexia-chat-gateway):
- POST /api/v1/chat/submit
- GET  /api/v1/chat/status/{request_id}
- GET  /api/v1/chat/result/{request_id}
- POST /api/v1/callbacks/strategy (protegido por X-Callback-Token)
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.callback_security import validate_callback_token
from ..database import get_db
from ..schemas.chat_gateway import (
    CallbackAckResponse,
    ChatResultResponse,
    ChatStatusResponse,
    ChatSubmitRequest,
    ChatSubmitResponse,
    StrategyCallbackRequest,
)
from ..services.chat_gateway_service import (
    get_chat_result,
    get_chat_status,
    process_strategy_callback,
    submit_chat,
    trigger_n8n_chat_workflow,
)

chat_router = APIRouter(prefix="/api/v1/chat", tags=["Chat Gateway"])
callbacks_router = APIRouter(prefix="/api/v1/callbacks", tags=["Callbacks n8n"])


@chat_router.post("/submit", response_model=ChatSubmitResponse)
async def chat_submit(
    payload: ChatSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Recibe mensaje del usuario, crea analysis_request, dispara el workflow n8n
    y devuelve request_id para consultar status/result.
    """
    request_id, n8n_payload = submit_chat(db, payload)
    try:
        await trigger_n8n_chat_workflow(n8n_payload)
    except Exception as exc:
        from ..models.analysis_request import AnalysisRequest
        ar = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
        if ar:
            ar.status = "failed"
            ar.progress = 100
            ar.current_stage = "n8n_trigger_failed"
            ar.error_code = "N8N_TRIGGER_ERROR"
            ar.error_message = str(exc)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not trigger n8n workflow: {exc}",
        ) from exc
    return ChatSubmitResponse(
        success=True,
        request_id=request_id,
        status="processing",
        message="Solicitud recibida y en proceso",
    )


@chat_router.get("/status/{request_id}", response_model=ChatStatusResponse)
def chat_status(
    request_id: str,
    db: Session = Depends(get_db),
):
    """Devuelve el estado de la solicitud (progress, current_stage, error, etc.)."""
    ar = get_chat_status(db, request_id)
    return ChatStatusResponse(
        success=True,
        request_id=ar.request_id,
        status=ar.status,
        progress=ar.progress,
        current_stage=ar.current_stage,
        error_code=ar.error_code,
        error_message=ar.error_message,
        created_at=ar.created_at,
        updated_at=ar.updated_at,
        completed_at=ar.completed_at,
    )


@chat_router.get("/result/{request_id}", response_model=ChatResultResponse)
def chat_result(
    request_id: str,
    db: Session = Depends(get_db),
):
    """Devuelve el resultado consolidado del análisis si está disponible."""
    ar, result = get_chat_result(db, request_id)
    result_json = None
    executive_summary = None
    if result:
        import json
        raw = result.result_json
        try:
            result_json = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            result_json = {}
        executive_summary = result.executive_summary
    return ChatResultResponse(
        success=True,
        request_id=ar.request_id,
        status=ar.status,
        result=result_json,
        executive_summary=executive_summary,
    )


def _parse_completed_at(completed_at: str | None) -> datetime | None:
    if not completed_at:
        return None
    try:
        return datetime.fromisoformat(completed_at.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


@callbacks_router.post(
    "/strategy",
    response_model=CallbackAckResponse,
    dependencies=[Depends(validate_callback_token)],
)
def strategy_callback(
    payload: StrategyCallbackRequest,
    db: Session = Depends(get_db),
):
    """
    Callback que n8n invoca al terminar el workflow (formato gateway).
    Requiere header X-Callback-Token = CALLBACK_SHARED_TOKEN.
    """
    err = payload.error or {}
    process_strategy_callback(
        db,
        request_id=payload.request_id,
        project_id=payload.project_id,
        status_value=payload.status,
        progress=payload.progress,
        current_stage=payload.current_stage,
        completed_at=_parse_completed_at(payload.completed_at),
        workflow_version=payload.workflow_version,
        engine_version=payload.engine_version,
        result=payload.result,
        error_code=err.get("code"),
        error_message=err.get("message"),
    )
    return CallbackAckResponse(
        success=True,
        message="Callback procesado correctamente",
        request_id=payload.request_id,
    )
