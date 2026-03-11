"""
API endpoints híbridos que combinan agentes especializados con el sistema existente
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
import os

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..services.hybrid_chatbot_service import hybrid_chatbot_service

logger = logging.getLogger(__name__)

router = APIRouter()

class HybridIntentRequest(BaseModel):
    message: str
    conversation_context: Dict[str, Any]

class HybridBMCRequest(BaseModel):
    business_idea: str
    use_high_quality: bool = False

class HybridBusinessPlanRequest(BaseModel):
    business_idea: str

class HybridMarketingPlanRequest(BaseModel):
    business_idea: str

@router.post("/detect-intent")
async def hybrid_detect_intent(
    request: HybridIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detecta intención usando agentes especializados con fallback al sistema anterior
    """
    try:
        result = await hybrid_chatbot_service.detect_intent_with_agents(
            request.message,
            request.conversation_context
        )
        
        return {
            "status": "success",
            "message": "Intención detectada exitosamente",
            "data": result,
            "method": "agents" if hybrid_chatbot_service.use_agents else "fallback"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detectando intención: {str(e)}"
        )

@router.post("/generate-bmc")
async def hybrid_generate_bmc(
    request: HybridBMCRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera BMC usando agentes especializados con fallback al sistema anterior
    """
    try:
        result = await hybrid_chatbot_service.generate_bmc_with_agents(
            request.business_idea,
            request.use_high_quality
        )
        
        return {
            "status": "success",
            "message": "Business Model Canvas generado exitosamente",
            "data": result,
            "method": "agents" if hybrid_chatbot_service.use_agents else "fallback"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando BMC: {str(e)}"
        )

@router.post("/generate-business-plan")
async def hybrid_generate_business_plan(
    request: HybridBusinessPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera plan de negocio usando agentes especializados con fallback
    """
    try:
        result = await hybrid_chatbot_service.generate_business_plan_with_agents(
            request.business_idea
        )
        
        # Si se especifica un proyecto, crear el documento PDF
        document_id = None
        if request.project_id:
            try:
                from ..utils.pdf_generator import generate_business_plan_pdf, create_project_directory, generate_unique_filename
                from ..models.project import Project
                from ..models.document import ProjectDocument
                from ..config import settings
                
                # Obtener información del proyecto
                project = db.query(Project).filter(Project.id == request.project_id).first()
                if project:
                    # Crear directorio del proyecto
                    project_dir = create_project_directory(request.project_id, settings.UPLOAD_DIR)
                    
                    # Generar nombre único para el archivo
                    filename = generate_unique_filename(f"Plan_Negocio_{project.name}")
                    file_path = os.path.join(project_dir, filename)
                    
                    # Generar PDF
                    generate_business_plan_pdf(result, project.name, file_path)
                    
                    # Crear registro en base de datos
                    db_document = ProjectDocument(
                        filename=f"Plan de Negocio - {project.name}",
                        original_filename=filename,
                        file_path=file_path,
                        file_type=".pdf",
                        file_size=os.path.getsize(file_path),
                        description=f"Plan de negocio generado automáticamente para {project.name}",
                        project_id=request.project_id,
                        uploader_id=current_user.id
                    )
                    
                    db.add(db_document)
                    db.commit()
                    db.refresh(db_document)
                    
                    document_id = db_document.id
                    
            except Exception as pdf_error:
                logger.warning(f"Error creando PDF del plan de negocio: {pdf_error}")
        
        return {
            "status": "success",
            "message": "Plan de negocio generado exitosamente",
            "data": result,
            "method": "agents" if hybrid_chatbot_service.use_agents else "fallback",
            "document_id": document_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan de negocio: {str(e)}"
        )

@router.post("/generate-marketing-plan")
async def hybrid_generate_marketing_plan(
    request: HybridMarketingPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Genera plan de marketing usando agentes especializados con fallback
    """
    try:
        result = await hybrid_chatbot_service.generate_marketing_plan_with_agents(
            request.business_idea
        )
        
        # Si se especifica un proyecto, crear el documento PDF
        document_id = None
        if request.project_id:
            try:
                from ..utils.pdf_generator import generate_marketing_plan_pdf, create_project_directory, generate_unique_filename
                from ..models.project import Project
                from ..models.document import ProjectDocument
                from ..config import settings
                
                # Obtener información del proyecto
                project = db.query(Project).filter(Project.id == request.project_id).first()
                if project:
                    # Crear directorio del proyecto
                    project_dir = create_project_directory(request.project_id, settings.UPLOAD_DIR)
                    
                    # Generar nombre único para el archivo
                    filename = generate_unique_filename(f"Plan_Marketing_{project.name}")
                    file_path = os.path.join(project_dir, filename)
                    
                    # Generar PDF
                    generate_marketing_plan_pdf(result, project.name, file_path)
                    
                    # Crear registro en base de datos
                    db_document = ProjectDocument(
                        filename=f"Plan de Marketing - {project.name}",
                        original_filename=filename,
                        file_path=file_path,
                        file_type=".pdf",
                        file_size=os.path.getsize(file_path),
                        description=f"Plan de marketing generado automáticamente para {project.name}",
                        project_id=request.project_id,
                        uploader_id=current_user.id
                    )
                    
                    db.add(db_document)
                    db.commit()
                    db.refresh(db_document)
                    
                    document_id = db_document.id
                    
            except Exception as pdf_error:
                logger.warning(f"Error creando PDF del plan de marketing: {pdf_error}")
        
        return {
            "status": "success",
            "message": "Plan de marketing generado exitosamente",
            "data": result,
            "method": "agents" if hybrid_chatbot_service.use_agents else "fallback",
            "document_id": document_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan de marketing: {str(e)}"
        )

@router.post("/toggle-agents")
async def toggle_agents(
    enabled: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Habilita o deshabilita el uso de agentes especializados
    """
    try:
        if enabled:
            hybrid_chatbot_service.enable_agents()
            message = "Agentes especializados habilitados"
        else:
            hybrid_chatbot_service.disable_agents()
            message = "Agentes especializados deshabilitados"
        
        return {
            "status": "success",
            "message": message,
            "agents_enabled": hybrid_chatbot_service.use_agents
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error configurando agentes: {str(e)}"
        )

@router.get("/status")
async def get_hybrid_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el estado actual del sistema híbrido
    """
    try:
        return {
            "status": "success",
            "data": {
                "agents_enabled": hybrid_chatbot_service.use_agents,
                "available_agents": list(hybrid_chatbot_service.agents_service.agents.keys()),
                "fallback_available": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}"
        )

