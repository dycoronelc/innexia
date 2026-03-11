"""
API endpoints para el sistema de agentes OpenAI
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.agents_service import agents_service

router = APIRouter()

class IntentDetectionRequest(BaseModel):
    message: str
    conversation_context: Dict[str, Any]

class BMCGenerationRequest(BaseModel):
    business_idea: str
    use_high_quality: bool = False

class BusinessPlanRequest(BaseModel):
    business_idea: str

class MarketingPlanRequest(BaseModel):
    business_idea: str

class ProjectAnalysisRequest(BaseModel):
    project_data: Dict[str, Any]

@router.post("/detect-intent")
async def detect_user_intent(
    request: IntentDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detecta la intención del usuario usando agentes especializados
    """
    try:
        result = await agents_service.detect_intent(
            request.message,
            request.conversation_context
        )
        
        return {
            "status": "success",
            "message": "Intención detectada exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detectando intención: {str(e)}"
        )

@router.post("/generate-bmc")
async def generate_bmc_with_agent(
    request: BMCGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera Business Model Canvas usando agente especializado
    """
    try:
        result = await agents_service.generate_bmc(
            request.business_idea,
            request.use_high_quality
        )
        
        return {
            "status": "success",
            "message": "Business Model Canvas generado exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando BMC: {str(e)}"
        )

@router.post("/generate-business-plan")
async def generate_business_plan_with_agent(
    request: BusinessPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera plan de negocio usando agente especializado
    """
    try:
        result = await agents_service.generate_business_plan(
            request.business_idea
        )
        
        return {
            "status": "success",
            "message": "Plan de negocio generado exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan de negocio: {str(e)}"
        )

@router.post("/generate-marketing-plan")
async def generate_marketing_plan_with_agent(
    request: MarketingPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera plan de marketing usando agente especializado
    """
    try:
        result = await agents_service.generate_marketing_plan(
            request.business_idea
        )
        
        return {
            "status": "success",
            "message": "Plan de marketing generado exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan de marketing: {str(e)}"
        )

@router.post("/analyze-project")
async def analyze_project_with_agent(
    request: ProjectAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analiza proyecto usando agente especializado
    """
    try:
        result = await agents_service.analyze_project(
            request.project_data
        )
        
        return {
            "status": "success",
            "message": "Proyecto analizado exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analizando proyecto: {str(e)}"
        )

