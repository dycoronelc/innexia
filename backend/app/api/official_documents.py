from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
from app.database import get_db
from app.core.auth import get_current_user
from app.models.official_document import OfficialDocument, DocumentType, DocumentCategory, ApprovalStatus
from app.models.user import User
from sqlalchemy import func

router = APIRouter()

# Configuración de archivos
UPLOAD_DIR = "uploads/documents"
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Crear directorio si no existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[dict])
async def get_official_documents(
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    document_type: Optional[str] = Query(None, description="Tipo de documento"),
    category: Optional[str] = Query(None, description="Categoría del documento"),
    status: Optional[str] = Query(None, description="Estado de aprobación"),
    limit: int = Query(20, ge=1, le=100, description="Número de elementos por página"),
    offset: int = Query(0, ge=0, description="Número de elementos a saltar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista de documentos oficiales con filtros opcionales
    """
    query = db.query(OfficialDocument)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            OfficialDocument.title.ilike(f"%{search}%") |
            OfficialDocument.description.ilike(f"%{search}%")
        )
    
    if document_type:
        query = query.filter(OfficialDocument.document_type == document_type)
    
    if category:
        query = query.filter(OfficialDocument.category == category)
    
    if status:
        query = query.filter(OfficialDocument.approval_status == status)
    
    # Solo mostrar documentos aprobados para usuarios normales
    if current_user.role not in ["admin", "document_approver"]:
        query = query.filter(OfficialDocument.approval_status == ApprovalStatus.APPROVED)
        query = query.filter(OfficialDocument.is_public == True)
    
    # Aplicar paginación
    total = query.count()
    documents = query.offset(offset).limit(limit).all()
    
    # Convertir a formato de respuesta
    result = []
    for doc in documents:
        result.append({
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "document_type": doc.document_type,
            "category": doc.category,
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "version": doc.version,
            "approval_status": doc.approval_status,
            "created_at": doc.created_at,
            "created_by": doc.created_by,
            "download_count": doc.download_count,
            "view_count": doc.view_count
        })
    
    return result

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_official_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: DocumentType = Form(...),
    category: DocumentCategory = Form(...),
    version: str = Form("1.0"),
    is_public: bool = Form(False),
    requires_approval: bool = Form(True),
    expires_at: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear nuevo documento oficial
    """
    # Verificar permisos
    if current_user.role not in ["admin", "document_creator", "document_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear documentos oficiales"
        )
    
    # Validar archivo
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo requerido"
        )
    
    # Verificar extensión
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Tipos válidos: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Verificar tamaño
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Guardar archivo
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )
    
    # Procesar tags
    tags_list = []
    if tags:
        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Crear documento en base de datos
    db_document = OfficialDocument(
        title=title,
        description=description,
        document_type=document_type,
        category=category,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        file_type=file_ext[1:],  # Sin el punto
        version=version,
        is_public=is_public,
        requires_approval=requires_approval,
        approval_status=ApprovalStatus.DRAFT if requires_approval else ApprovalStatus.APPROVED,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        tags=tags_list,
        created_by=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return {
        "id": db_document.id,
        "title": db_document.title,
        "file_name": db_document.file_name,
        "status": db_document.approval_status,
        "message": "Documento creado exitosamente"
    }

@router.get("/{document_id}", response_model=dict)
async def get_official_document_by_id(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener documento oficial específico por ID
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar acceso
    if document.approval_status != ApprovalStatus.APPROVED and current_user.role not in ["admin", "document_approver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este documento"
        )
    
    # Incrementar contador de vistas
    document.view_count += 1
    db.commit()
    
    return {
        "id": document.id,
        "title": document.title,
        "description": document.description,
        "document_type": document.document_type,
        "category": document.category,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "file_type": document.file_type,
        "version": document.version,
        "approval_status": document.approval_status,
        "is_public": document.is_public,
        "requires_approval": document.requires_approval,
        "expires_at": document.expires_at,
        "tags": document.tags,
        "document_metadata": document.document_metadata,
        "download_count": document.download_count,
        "view_count": document.view_count,
        "created_at": document.created_at,
        "created_by": document.created_by,
        "approved_by": document.approved_by,
        "approved_at": document.approved_at
    }

@router.post("/{document_id}/download")
async def download_official_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Descargar documento oficial
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar acceso
    if document.approval_status != ApprovalStatus.APPROVED and current_user.role not in ["admin", "document_approver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este documento"
        )
    
    # Verificar si el archivo existe
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado en el servidor"
        )
    
    # Incrementar contador de descargas
    document.download_count += 1
    db.commit()
    
    # Retornar información del archivo para descarga
    return {
        "file_path": document.file_path,
        "file_name": document.file_name,
        "file_type": document.file_type,
        "file_size": document.file_size
    }

@router.put("/{document_id}", response_model=dict)
async def update_official_document(
    document_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document_type: Optional[DocumentType] = Form(None),
    category: Optional[DocumentCategory] = Form(None),
    version: Optional[str] = Form(None),
    is_public: Optional[bool] = Form(None),
    requires_approval: Optional[bool] = Form(None),
    expires_at: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar documento oficial existente
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "document_editor"] and document.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este documento"
        )
    
    # Actualizar campos
    if title is not None:
        document.title = title
    if description is not None:
        document.description = description
    if document_type is not None:
        document.document_type = document_type
    if category is not None:
        document.category = category
    if version is not None:
        document.version = version
    if is_public is not None:
        document.is_public = is_public
    if requires_approval is not None:
        document.requires_approval = requires_approval
    if expires_at is not None:
        document.expires_at = datetime.fromisoformat(expires_at) if expires_at else None
    if tags is not None:
        document.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    document.updated_at = func.now()
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "title": document.title,
        "message": "Documento actualizado exitosamente"
    }

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_official_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar documento oficial
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "document_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar documentos"
        )
    
    # Eliminar archivo físico
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log del error pero continuar con la eliminación de la base de datos
        print(f"Error al eliminar archivo: {e}")
    
    # Eliminar de la base de datos
    db.delete(document)
    db.commit()
    
    return None

@router.post("/{document_id}/approve", response_model=dict)
async def approve_official_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aprobar documento oficial
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "document_approver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para aprobar documentos"
        )
    
    # Cambiar estado a aprobado
    document.approval_status = ApprovalStatus.APPROVED
    document.approved_by = current_user.id
    document.approved_at = func.now()
    
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "title": document.title,
        "status": document.approval_status,
        "message": "Documento aprobado exitosamente"
    }

@router.post("/{document_id}/reject", response_model=dict)
async def reject_official_document(
    document_id: int,
    reason: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rechazar documento oficial
    """
    document = db.query(OfficialDocument).filter(OfficialDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "document_approver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para rechazar documentos"
        )
    
    # Cambiar estado a rechazado
    document.approval_status = ApprovalStatus.REJECTED
    document.approved_by = current_user.id
    document.approved_at = func.now()
    
    # Agregar razón del rechazo en document_metadata
    if not document.document_metadata:
        document.document_metadata = {}
    document.document_metadata["rejection_reason"] = reason
    document.document_metadata["rejected_by"] = current_user.id
    document.document_metadata["rejected_at"] = datetime.now().isoformat()
    
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "title": document.title,
        "status": document.approval_status,
        "message": "Documento rechazado exitosamente"
    }
