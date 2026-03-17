"""
Servicios del chat gateway: submit (disparo n8n), status, result y procesamiento del callback
en formato StrategyCallbackRequest (compatible con innexia-chat-gateway).
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..config import settings
from ..models.analysis_request import AnalysisRequest
from ..models.analysis_result import AnalysisResult
from ..schemas.chat_gateway import ChatSubmitRequest
from ..utils.ids import generate_request_id
from .strategy_engine_persistence import sync_result_to_project


async def trigger_n8n_chat_workflow(payload: Dict[str, Any]) -> None:
    """Dispara el workflow de n8n con el payload del chat (request_id, message, callback_url, etc.)."""
    url = settings.N8N_WEBHOOK_URL or settings.N8N_STRATEGY_ENGINE_WEBHOOK_URL
    if not url:
        raise ValueError("N8N_WEBHOOK_URL o N8N_STRATEGY_ENGINE_WEBHOOK_URL no configurada")
    import httpx
    timeout = httpx.Timeout(settings.N8N_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()


def submit_chat(db: Session, payload: ChatSubmitRequest) -> str:
    """
    Crea analysis_request, dispara n8n con callback_url y devuelve request_id.
    """
    request_id = generate_request_id()
    metadata = payload.metadata or {}
    session_id = metadata.get("session_id") if isinstance(metadata, dict) else None

    project_name = (payload.message or "")[:200].strip() or "Chat analysis"
    input_json = payload.model_dump(mode="json")
    input_json["request_id"] = request_id

    ar = AnalysisRequest(
        request_id=request_id,
        project_id=str(payload.project_id) if payload.project_id is not None else None,
        project_name=project_name,
        analysis_type=payload.analysis_type or "full_strategy",
        language_code=payload.language_code or "es",
        organization_name=payload.organization_name,
        input_json=json.dumps(input_json, ensure_ascii=False),
        input_message=payload.message,
        status="running",
        workflow_version=settings.N8N_WORKFLOW_VERSION or "v1",
        progress=10,
        current_stage="workflow_triggered",
        callback_url=payload.callback_url,
        user_id=str(payload.user_id) if payload.user_id is not None else None,
        session_id=str(session_id) if session_id is not None else None,
    )
    db.add(ar)
    db.commit()
    db.refresh(ar)

    # Payload esperado por IASE_CHAT_WEBHOOK_ASYNC: request_id, project_name, input_brief, callback_url, etc.
    org_name = payload.organization_name or "Innexia"
    n8n_payload = {
        "request_id": request_id,
        "project_id": str(payload.project_id) if payload.project_id is not None else None,
        "project_name": project_name,
        "analysis_type": payload.analysis_type or "full_strategy",
        "language": payload.language_code or "es",
        "organization": {"name": org_name, "industry": "tecnologia y salud", "country": "Panama"},
        "input_brief": {
            "title": project_name,
            "description": payload.message or "",
            "objective": "Generar análisis estratégico",
            "problem_statement": payload.message or "",
            "constraints": [],
        },
        "execution_options": {
            "run_modules": ["market_intelligence", "bmc", "strategy", "finance", "risks", "roadmap", "verdict", "activities"],
            "generate_kanban": True,
            "generate_gantt": True,
            "persist_outputs": True,
            "strict_json": True,
        },
        "chat_context": {
            "session_id": str(session_id) if session_id else None,
            "user_id": str(payload.user_id) if payload.user_id else None,
            "project_id": str(payload.project_id) if payload.project_id is not None else None,
            "original_message": payload.message or "",
        },
        "callback_url": payload.callback_url,
        "meta": {
            **(payload.metadata or {}),
            "workflow_version": settings.N8N_WORKFLOW_VERSION or "v2.3-chat-webhook-async",
            "source": "fastapi_chat_submit",
        },
    }
    return request_id, n8n_payload


def get_chat_status(db: Session, request_id: str) -> AnalysisRequest:
    """Devuelve el analysis_request para el request_id."""
    ar = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if not ar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    return ar


def get_chat_result(db: Session, request_id: str) -> Tuple[AnalysisRequest, Optional[AnalysisResult]]:
    """Devuelve analysis_request y analysis_result (si existe)."""
    ar = get_chat_status(db, request_id)
    result = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
    return ar, result


def _gateway_result_to_body(payload_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte el result del callback gateway (business_model_canvas, financials, etc.)
    al formato body que esperan nuestros mapeos (bmc, finance, etc.).
    """
    return {
        "request_id": payload_result.get("request_id"),
        "project_name": payload_result.get("project_name"),
        "status": payload_result.get("status", "completed"),
        "workflow_version": payload_result.get("workflow_version"),
        "meta": payload_result.get("meta") or {},
        "supervisor": payload_result.get("supervisor"),
        "market_analysis": payload_result.get("market_analysis"),
        "bmc": payload_result.get("business_model_canvas") or payload_result.get("bmc"),
        "strategy": payload_result.get("strategy"),
        "finance": payload_result.get("financials") or payload_result.get("finance"),
        "risks": payload_result.get("risks"),
        "roadmap": payload_result.get("roadmap"),
        "verdict": payload_result.get("verdict"),
        "activities": payload_result.get("activities"),
        "kanban": payload_result.get("kanban"),
        "gantt": payload_result.get("gantt"),
        "summary": {
            "executive_summary": payload_result.get("executive_summary"),
            "key_findings": payload_result.get("key_findings"),
            "priority_actions": payload_result.get("priority_actions"),
        }
        if payload_result.get("executive_summary") or payload_result.get("key_findings")
        else payload_result.get("summary"),
    }


def process_strategy_callback(
    db: Session,
    request_id: str,
    project_id: Optional[int],
    status_value: str,
    progress: Optional[int],
    current_stage: Optional[str],
    completed_at: Optional[datetime],
    workflow_version: Optional[str],
    engine_version: Optional[str],
    result: Optional[Dict[str, Any]],
    error_code: Optional[str],
    error_message: Optional[str],
) -> None:
    """
    Actualiza analysis_request y analysis_result a partir del callback de n8n (formato gateway).
    Si hay result y project_id, sincroniza a project_agent_output y tablas canónicas.
    """
    ar = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if not ar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )

    status_map = {"queued": "pending", "processing": "running", "completed": "completed", "failed": "failed"}
    db_status = status_map.get(status_value, status_value)
    if db_status not in ("pending", "running", "completed", "failed"):
        db_status = "completed" if status_value == "completed" else "running"

    ar.status = db_status
    if progress is not None:
        ar.progress = progress
    if current_stage is not None:
        ar.current_stage = current_stage
    if completed_at is not None:
        ar.completed_at = completed_at
    if workflow_version is not None:
        ar.workflow_version = workflow_version
    if error_code is not None:
        ar.error_code = error_code
    if error_message is not None:
        ar.error_message = error_message
    db.commit()
    db.refresh(ar)

    if result:
        body = _gateway_result_to_body({**result, "request_id": request_id, "status": db_status})
        consolidated = json.dumps(body, ensure_ascii=False)
        executive = result.get("executive_summary")

        existing = db.query(AnalysisResult).filter(AnalysisResult.request_id == request_id).first()
        if existing:
        existing.result_json = consolidated
        existing.executive_summary = executive
    else:
        db.add(
            AnalysisResult(
                request_id=request_id,
                result_json=consolidated,
                executive_summary=executive,
            )
        )
        db.commit()

        pid = project_id or (ar.project_id if ar else None)
        if pid is not None:
            sync_result_to_project(
                db,
                project_id=int(pid),
                request_id=request_id,
                result=body,
                status=db_status,
                modules_executed=body.get("meta", {}).get("modules_executed"),
                modules_failed=body.get("meta", {}).get("modules_failed"),
            )
