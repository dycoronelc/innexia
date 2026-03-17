import time
from typing import Any, Dict, List, Optional, Union

import httpx
from sqlalchemy.orm import Session

from ..config import settings
from ..schemas.analysis_engine import OpportunityRequest
from .strategy_engine_request_builder import build_engine_payload
from .strategy_engine_persistence import (
    create_analysis_request,
    mark_analysis_completed,
    mark_analysis_failed,
    save_analysis_result,
    save_analysis_modules,
    replace_analysis_activities,
    replace_analysis_risks,
    sync_result_to_project,
)


def extract_body_from_n8n_response(response_data: Union[Dict[str, Any], List[Any]]) -> Dict[str, Any]:
    """
    Extrae el cuerpo útil del JSON que devuelve el workflow n8n.
    Acepta: array con [{ "response": { "body": {...} } }] o { "response": { "body": {...} } } o { "result": {...} } o {...}.
    """
    if isinstance(response_data, list):
        if not response_data:
            return {}
        data = response_data[0]
    else:
        data = response_data or {}

    if not isinstance(data, dict):
        return {}

    # response.body (estructura típica de n8n)
    response = data.get("response")
    if isinstance(response, dict):
        body = response.get("body")
        if isinstance(body, dict):
            return body

    # body directo
    if isinstance(data.get("body"), dict):
        return data["body"]

    # result directo
    if isinstance(data.get("result"), dict):
        return data["result"]

    return data


async def call_n8n_strategy_engine(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not settings.N8N_STRATEGY_ENGINE_WEBHOOK_URL:
        raise ValueError("N8N_STRATEGY_ENGINE_WEBHOOK_URL no está configurada")
    timeout = httpx.Timeout(settings.N8N_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(settings.N8N_STRATEGY_ENGINE_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        return response.json()


async def analyze_opportunity(
    db: Session,
    *,
    data: OpportunityRequest,
    project_id: Optional[int] = None,
) -> Dict[str, Any]:
    payload = build_engine_payload(data)
    request_id = payload["request_id"]
    workflow_version = payload.get("meta", {}).get("workflow_version", settings.N8N_WORKFLOW_VERSION)
    start = time.perf_counter()

    create_analysis_request(
        db,
        request_id=request_id,
        project_id=project_id,
        project_name=payload["project_name"],
        analysis_type=payload.get("analysis_type"),
        language_code=payload.get("language", "es"),
        organization_name=(payload.get("organization") or {}).get("name"),
        input_payload=payload,
        workflow_version=workflow_version,
        created_by=data.created_by,
    )

    try:
        response_data = await call_n8n_strategy_engine(payload)
        result = extract_body_from_n8n_response(response_data)

        save_analysis_result(db, request_id=request_id, result=result)
        save_analysis_modules(db, request_id=request_id, result=result)
        gantt = result.get("gantt") or {}
        replace_analysis_activities(
            db,
            request_id=request_id,
            activities=result.get("activities") or [],
            gantt_tasks=gantt.get("tasks"),
        )
        replace_analysis_risks(db, request_id=request_id, risks=result.get("risks") or [])

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if project_id is not None:
            meta = result.get("meta") or {}
            sync_result_to_project(
                db,
                project_id=project_id,
                request_id=request_id,
                result=result,
                execution_time_ms=elapsed_ms or meta.get("execution_time_ms"),
                modules_executed=meta.get("modules_executed"),
                modules_failed=meta.get("modules_failed"),
            )

        mark_analysis_completed(db, request_id=request_id, execution_time_ms=elapsed_ms)

        return {
            "request_id": request_id,
            "status": result.get("status", "completed"),
            "result": result,
        }
    except Exception as e:
        mark_analysis_failed(db, request_id=request_id, error_message=str(e))
        raise
