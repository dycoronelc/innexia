"""
API para manejar entrevistas guiadas de negocios y generación de documentos
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
import time

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.document import GeneratedDocument, DocumentGenerationLog
from ..services.business_interview_service import BusinessInterviewService, BusinessInterviewData
from ..services.pdf_generation_service import PDFGenerationService, DocumentRequest, DocumentType

logger = logging.getLogger(__name__)

# Almacenamiento temporal en memoria para las entrevistas
# En producción, esto debería ser una base de datos o Redis
interview_sessions: Dict[str, Dict[str, Any]] = {}

router = APIRouter(prefix="/api/business-interview", tags=["business-interview"])

# ============================================================================
# SCHEMAS PARA LA ENTREVISTA DE NEGOCIOS
# ============================================================================

class InterviewQuestionResponse(BaseModel):
    id: str
    question: str
    field: str
    type: str
    options: Optional[List[str]] = None
    required: bool = True

class InterviewAnswerRequest(BaseModel):
    field: str
    value: Any
    session_id: Optional[str] = None

class InterviewProgressResponse(BaseModel):
    current_question: Optional[InterviewQuestionResponse]
    progress_percentage: float
    completed_fields: List[str]
    remaining_fields: List[str]
    is_complete: bool
    session_id: Optional[str] = None

class CompleteInterviewRequest(BaseModel):
    business_data: Dict[str, Any]
    project_id: Optional[int] = None

class GenerateDocumentsRequest(BaseModel):
    project_id: int
    business_data: Dict[str, Any]
    document_types: Optional[List[str]] = None  # Si no se especifica, genera todos

class DocumentResponse(BaseModel):
    document_id: str
    title: str
    document_type: str
    file_path: Optional[str] = None
    generated_at: str
    download_count: int = 0

# ============================================================================
# ENDPOINTS PARA LA ENTREVISTA
# ============================================================================

@router.post("/start", response_model=InterviewProgressResponse)
async def start_interview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Inicia una nueva entrevista de negocio"""
    try:
        # Crear una sesión única para esta entrevista
        session_id = f"{current_user.id}_{int(time.time())}"
        interview_sessions[session_id] = {
            'user_id': current_user.id,
            'answers': {},
            'created_at': time.time()
        }
        
        interview_service = BusinessInterviewService()
        next_question = interview_service.get_next_question({})
        
        if next_question:
            question_response = InterviewQuestionResponse(
                id=next_question.id,
                question=next_question.question,
                field=next_question.field,
                type=next_question.type,
                options=next_question.options,
                required=next_question.required
            )
        else:
            question_response = None
        
        return InterviewProgressResponse(
            current_question=question_response,
            progress_percentage=interview_service.get_completion_percentage(),
            completed_fields=list(interview_service.completed_fields),
            remaining_fields=[q.field for q in interview_service.questions if q.field not in interview_service.completed_fields],
            is_complete=interview_service.is_interview_complete(),
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error iniciando entrevista: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error iniciando entrevista: {str(e)}"
        )

@router.post("/answer", response_model=InterviewProgressResponse)
async def answer_question(
    answer: InterviewAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Responde una pregunta de la entrevista"""
    try:
        interview_service = BusinessInterviewService()
        
        # Buscar la sesión de entrevista
        session_id = answer.session_id
        if not session_id or session_id not in interview_sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sesión de entrevista no encontrada"
            )
        
        # Actualizar la sesión con la nueva respuesta
        interview_sessions[session_id]['answers'][answer.field] = answer.value
        current_data = interview_sessions[session_id]['answers']
        
        logger.info(f"Respuesta recibida: {answer.field} = {answer.value}")
        logger.info(f"Datos actuales: {current_data}")
        
        # Actualizar el servicio con todos los datos de la sesión
        interview_service._update_interview_data(current_data)
        
        # Obtener la siguiente pregunta
        next_question = interview_service.get_next_question(current_data)
        logger.info(f"Siguiente pregunta: {next_question.field if next_question else 'None'}")
        logger.info(f"Campos completados: {interview_service.completed_fields}")
        logger.info(f"¿Entrevista completa?: {interview_service.is_interview_complete()}")
        
        if next_question:
            question_response = InterviewQuestionResponse(
                id=next_question.id,
                question=next_question.question,
                field=next_question.field,
                type=next_question.type,
                options=next_question.options,
                required=next_question.required
            )
        else:
            question_response = None
        
        return InterviewProgressResponse(
            current_question=question_response,
            progress_percentage=interview_service.get_completion_percentage(),
            completed_fields=list(interview_service.completed_fields),
            remaining_fields=[q.field for q in interview_service.questions if q.field not in interview_service.completed_fields],
            is_complete=interview_service.is_interview_complete()
        )
        
    except Exception as e:
        logger.error(f"Error respondiendo pregunta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error respondiendo pregunta: {str(e)}"
        )

@router.get("/debug/{session_id}")
async def debug_session(session_id: str):
    """Endpoint de debug para ver el estado de una sesión"""
    if session_id not in interview_sessions:
        return {"error": "Sesión no encontrada"}
    
    session = interview_sessions[session_id]
    interview_service = BusinessInterviewService()
    interview_service._update_interview_data(session['answers'])
    
    return {
        "session_id": session_id,
        "answers": session['answers'],
        "completed_fields": list(interview_service.completed_fields),
        "required_fields": [q.field for q in interview_service.questions if q.required],
        "is_complete": interview_service.is_interview_complete(),
        "missing_required": [q.field for q in interview_service.questions if q.required and q.field not in interview_service.completed_fields]
    }

@router.post("/complete", response_model=Dict[str, Any])
async def complete_interview(
    request: CompleteInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Completa la entrevista y genera el prompt para el BMC"""
    try:
        logger.info(f"Datos recibidos para completar entrevista: {request.business_data}")
        logger.info(f"Project ID: {request.project_id}")
        logger.info(f"Número de campos recibidos: {len(request.business_data)}")
        logger.info(f"Campos recibidos: {list(request.business_data.keys())}")
        
        interview_service = BusinessInterviewService()
        
        # Actualizar datos de la entrevista
        interview_service._update_interview_data(request.business_data)
        logger.info(f"Datos actualizados en el servicio: {interview_service.interview_data}")
        logger.info(f"Campos completados después de actualizar: {interview_service.completed_fields}")
        
        logger.info(f"Campos completados: {interview_service.completed_fields}")
        logger.info(f"¿Entrevista completa?: {interview_service.is_interview_complete()}")
        
        if not interview_service.is_interview_complete():
            missing_fields = [q.field for q in interview_service.questions if q.field not in interview_service.completed_fields]
            logger.warning(f"Campos faltantes: {missing_fields}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La entrevista no está completa. Faltan campos requeridos: {missing_fields}"
            )
        
        # Generar prompt para BMC
        logger.info("Generando prompt para BMC...")
        bmc_prompt = interview_service.generate_business_prompt()
        logger.info("Prompt para BMC generado exitosamente")
        
        # Generar prompts para documentos
        document_prompts = interview_service.generate_document_prompts()
        
        return {
            "message": "Entrevista completada exitosamente",
            "bmc_prompt": bmc_prompt,
            "document_prompts": document_prompts,
            "interview_summary": interview_service.get_interview_summary(),
            "business_data": interview_service.interview_data.dict()
        }
        
    except Exception as e:
        logger.error(f"Error completando entrevista: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completando entrevista: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA GENERACIÓN DE DOCUMENTOS
# ============================================================================

# TEMPORALMENTE COMENTADO - Servicio de PDF no disponible
# @router.post("/generate-documents", response_model=List[DocumentResponse])
# async def generate_documents(
#     request: GenerateDocumentsRequest,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Genera documentos basados en los datos de la entrevista"""
#     try:
#         # Verificar que el proyecto existe
#         project = db.query(Project).filter(
#             Project.id == request.project_id,
#             Project.owner_id == current_user.id
#         ).first()
#         
#         if not project:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Proyecto no encontrado"
#             )
#         
#         pdf_service = PDFGenerationService()
#         generated_documents = []
#         
#         # Determinar qué documentos generar
#         if request.document_types:
#             document_types = [DocumentType(dt) for dt in request.document_types]
#         else:
#             document_types = list(DocumentType)
#         
#         for doc_type in document_types:
#             try:
#                 # Crear solicitud de documento
#                 doc_request = DocumentRequest(
#                     document_type=doc_type,
#                     business_data=request.business_data,
#                     project_id=request.project_id,
#                     user_id=current_user.id
#                 )
#                 
#                 # Generar documento
#                 document = await pdf_service.generate_document(doc_request)
#                 
#                 # Guardar en base de datos
#                 db_document = GeneratedDocument(
#                     project_id=request.project_id,
#                     user_id=current_user.id,
#                     document_type=doc_type.value,
#                     title=document.title,
#                     content=document.content,
#                     file_path=document.file_path,
#                     file_size=len(document.content) if document.content else 0,
#                     metadata={
#                         "generated_at": document.generated_at.isoformat(),
#                         "business_data": request.business_data
#                     }
#                 )
#                 
#                 db.add(db_document)
#                 db.flush()  # Para obtener el ID
#                 
#                 # Registrar log de generación
#                 log_entry = DocumentGenerationLog(
#                     project_id=request.project_id,
#                     user_id=current_user.id,
#                     document_type=doc_type.value,
#                     status="success",
#                     generation_time=0,  # Se podría calcular el tiempo real
#                     model_used="gpt-3.5-turbo"
#                 )
#                 
#                 db.add(log_entry)
#                 
#                 generated_documents.append(DocumentResponse(
#                     document_id=str(db_document.id),
#                     title=document.title,
#                     document_type=doc_type.value,
#                     file_path=document.file_path,
#                     generated_at=document.generated_at.isoformat(),
#                     download_count=0
#                 ))
#                 
#             except Exception as e:
#                 logger.error(f"Error generando documento {doc_type}: {str(e)}")
#                 
#                 # Registrar log de error
#                 log_entry = DocumentGenerationLog(
#                     project_id=request.project_id,
#                     user_id=current_user.id,
#                     document_type=doc_type.value,
#                     status="error",
#                     error_message=str(e)
#                 )
#                 
#                 db.add(log_entry)
#                 continue
#         
#         db.commit()
#         
#         return generated_documents
#         
#     except Exception as e:
#         logger.error(f"Error generando documentos: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error generando documentos: {str(e)}"
#         )

@router.post("/generate-documents", response_model=List[DocumentResponse])
async def generate_documents(
    request: GenerateDocumentsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera documentos basados en los datos de la entrevista"""
    try:
        # Verificar que el proyecto existe y pertenece al usuario
        project = db.query(Project).filter(
            Project.id == request.project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proyecto no encontrado"
            )
        
        # Inicializar servicio de PDF
        pdf_service = PDFGenerationService()
        generated_documents = []
        
        # Generar cada tipo de documento solicitado
        for doc_type in request.document_types:
            try:
                # Crear solicitud de documento
                doc_request = DocumentRequest(
                    document_type=DocumentType(doc_type),
                    title=f"{doc_type.replace('_', ' ').title()}",
                    content=request.business_data,
                    project_name=project.name,
                    company_name="InnovAI",
                    author=f"Usuario: {current_user.email}"
                )
                
                # Generar PDF
                pdf_content = pdf_service.generate_document(doc_request)
                
                # Crear nombre de archivo único
                import uuid
                filename = f"{doc_type}_{request.project_id}_{uuid.uuid4().hex[:8]}.pdf"
                
                # Crear directorio del proyecto si no existe
                project_dir = os.path.join("uploads", str(request.project_id))
                os.makedirs(project_dir, exist_ok=True)
                
                # Guardar archivo PDF
                file_path = os.path.join(project_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Crear registro en base de datos
                document = GeneratedDocument(
                    title=f"{doc_type.replace('_', ' ').title()} - {project.name}",
                    document_type=doc_type,
                    file_path=file_path,
                    project_id=request.project_id,
                    generated_by=current_user.id
                )
                
                db.add(document)
                db.commit()
                db.refresh(document)
                
                # Agregar a la respuesta
                generated_documents.append(DocumentResponse(
                    document_id=str(document.id),
                    title=document.title,
                    document_type=document.document_type,
                    file_path=document.file_path,
                    generated_at=document.created_at.isoformat(),
                    download_count=document.download_count
                ))
                
                logger.info(f"Documento {doc_type} generado para proyecto {request.project_id}")
                
            except Exception as e:
                logger.error(f"Error generando documento {doc_type}: {str(e)}")
                continue
        
        if not generated_documents:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudieron generar documentos"
            )
        
        return generated_documents
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en generate_documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/documents/{project_id}", response_model=List[DocumentResponse])
async def get_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los documentos generados para un proyecto"""
    try:
        # Verificar que el proyecto existe y pertenece al usuario
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proyecto no encontrado"
            )
        
        # Obtener documentos
        documents = db.query(GeneratedDocument).filter(
            GeneratedDocument.project_id == project_id
        ).order_by(GeneratedDocument.created_at.desc()).all()
        
        return [
            DocumentResponse(
                document_id=str(doc.id),
                title=doc.title,
                document_type=doc.document_type,
                file_path=doc.file_path,
                generated_at=doc.created_at.isoformat(),
                download_count=doc.download_count
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo documentos: {str(e)}"
        )

@router.get("/download/{document_id}")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Descarga un documento específico"""
    try:
        # Obtener documento
        document = db.query(GeneratedDocument).filter(
            GeneratedDocument.id == document_id,
            GeneratedDocument.user_id == current_user.id
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Actualizar contador de descargas
        document.download_count += 1
        document.is_downloaded = True
        db.commit()
        
        # Retornar contenido del documento
        return {
            "title": document.title,
            "content": document.content,
            "document_type": document.document_type,
            "generated_at": document.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error descargando documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error descargando documento: {str(e)}"
        )

@router.get("/interview-summary")
async def get_interview_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene un resumen de la entrevista actual"""
    try:
        interview_service = BusinessInterviewService()
        return interview_service.get_interview_summary()
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de entrevista: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen de entrevista: {str(e)}"
        )
