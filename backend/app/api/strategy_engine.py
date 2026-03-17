from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..database import get_db
from ..models.analysis_request import AnalysisRequest
from ..models.project import Project
from ..models.user import User
from ..schemas.analysis_engine import OpportunityRequest, OpportunityResponse
from ..services.strategy_engine_persistence import get_analysis_result, persist_n8n_response
from ..services.strategy_engine_service import analyze_opportunity as analyze_opportunity_service, extract_body_from_n8n_response

router = APIRouter()


def _get_accessible_project(project_id: int, current_user: User, db: Session) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.company_id == current_user.company_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado",
        )
    return project


def _get_accessible_request(request_id: str, current_user: User, db: Session) -> AnalysisRequest:
    record = db.query(AnalysisRequest).filter(AnalysisRequest.request_id == request_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado",
        )

    if record.project_id is not None:
        _get_accessible_project(int(record.project_id), current_user, db)
    return record


@router.post("/analyze-opportunity", response_model=OpportunityResponse)
async def analyze_opportunity(
    body: OpportunityRequest,
    project_id: Optional[int] = Query(None, description="Proyecto existente a actualizar con el resultado"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Ejecuta el AI Strategy Engine para analizar una oportunidad y persiste la corrida por request_id.
    Si se envía project_id, también aterriza el resultado en project_agent_output y tablas canónicas.
    """
    if project_id is not None:
        _get_accessible_project(project_id, current_user, db)

    payload = body.model_copy(update={"created_by": current_user.username})
    try:
        response = await analyze_opportunity_service(
            db,
            data=payload,
            project_id=project_id,
        )
        return OpportunityResponse(**response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error ejecutando AI Strategy Engine: {str(e)}",
        )


@router.get("/analysis/{request_id}", response_model=OpportunityResponse)
async def get_analysis_by_request_id(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene el resultado consolidado de una corrida del AI Strategy Engine por request_id.
    """
    record = _get_accessible_request(request_id, current_user, db)
    result = get_analysis_result(db, request_id=request_id)

    return OpportunityResponse(
        request_id=record.request_id,
        status=record.status,
        result=result or {},
    )


@router.post(
    "/strategy-engine/callback",
    summary="Webhook: recibe resultado del workflow n8n",
    response_model=Dict[str, Any],
)
async def n8n_strategy_callback(
    payload: Any = Body(..., description="JSON que devuelve n8n (array o objeto con response.body)"),
    db: Session = Depends(get_db),
):
    """
    Recibe el JSON completo que retorna el workflow de n8n y actualiza toda la información en la BD:
    analysis_requests, analysis_results, analysis_modules, analysis_activities, analysis_risks,
    y si existe project_id (en la request previa o en el body), project_agent_output y tablas canónicas.

    Acepta el formato típico de n8n: `[{ "response": { "body": { ... } } }]` o directamente el objeto body.
    """
    body = extract_body_from_n8n_response(payload)
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo extraer el body del payload (se espera response.body o body o result)",
        )
    try:
        result = persist_n8n_response(db, body)
        if not result.get("ok"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Error al persistir"),
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error persistiendo resultado n8n: {str(e)}",
        )
