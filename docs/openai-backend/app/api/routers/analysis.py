from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analysis import OpportunityRequest, OpportunityResponse
from app.services.persistence_service import (
    create_analysis_request,
    get_analysis_result,
    mark_analysis_completed,
    mark_analysis_failed,
    replace_analysis_activities,
    replace_analysis_risks,
    save_analysis_modules,
    save_analysis_result,
)
from app.services.request_builder import build_engine_payload
from app.services.strategy_engine_service import call_n8n_strategy_engine

router = APIRouter()


@router.post("/analyze-opportunity", response_model=OpportunityResponse)
async def analyze_opportunity(
    payload: OpportunityRequest,
    db: Session = Depends(get_db),
):
    engine_payload = build_engine_payload(payload)
    request_id = engine_payload["request_id"]

    create_analysis_request(
        db,
        request_id=request_id,
        project_name=engine_payload["project_name"],
        analysis_type=engine_payload.get("analysis_type"),
        organization_name=engine_payload.get("organization", {}).get("name"),
        input_payload=engine_payload,
        workflow_version=engine_payload.get("meta", {}).get("workflow_version", "v5.2"),
        created_by=payload.created_by,
    )

    started = time.perf_counter()

    try:
        engine_result = await call_n8n_strategy_engine(engine_payload)

        if not isinstance(engine_result, dict):
            raise HTTPException(status_code=502, detail="Invalid response from AI Strategy Engine")

        # Normaliza el formato si n8n devuelve directamente el consolidado
        if "result" in engine_result and isinstance(engine_result["result"], dict):
            final_result = engine_result["result"]
            status = engine_result.get("status", "completed")
        else:
            final_result = engine_result
            status = final_result.get("status", "completed")

        save_analysis_result(db, request_id=request_id, result=final_result)
        save_analysis_modules(db, request_id=request_id, result=final_result)
        replace_analysis_activities(
            db,
            request_id=request_id,
            activities=final_result.get("activities", []),
        )
        replace_analysis_risks(
            db,
            request_id=request_id,
            risks=final_result.get("risks", []),
        )

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        mark_analysis_completed(db, request_id=request_id, execution_time_ms=elapsed_ms)

        return OpportunityResponse(
            request_id=request_id,
            status=status,
            result=final_result,
        )

    except HTTPException as exc:
        mark_analysis_failed(db, request_id=request_id, error_message=str(exc.detail))
        raise
    except Exception as exc:
        mark_analysis_failed(db, request_id=request_id, error_message=str(exc))
        raise HTTPException(status_code=500, detail=f"Strategy engine error: {exc}") from exc


@router.get("/analysis/{request_id}", response_model=OpportunityResponse)
def get_analysis(
    request_id: str,
    db: Session = Depends(get_db),
):
    result = get_analysis_result(db, request_id=request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return OpportunityResponse(
        request_id=request_id,
        status=result.get("status", "completed"),
        result=result,
    )
