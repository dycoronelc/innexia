import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..core.auth import get_current_user, get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.document import ProjectDocument
from ..models.audit_log import AuditLog
from ..schemas.document import ProjectDocumentCreate, ProjectDocumentUpdate, ProjectDocument as ProjectDocumentSchema
from ..config import settings

router = APIRouter()

def get_file_extension(filename: str) -> str:
    """Obtener extensión del archivo"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    """Verificar si el archivo tiene una extensión permitida"""
    return get_file_extension(filename) in settings.ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para el archivo"""
    extension = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{extension}"

def get_file_size_mb(file_size_bytes: int) -> float:
    """Convertir tamaño de archivo a MB"""
    return round(file_size_bytes / (1024 * 1024), 2)

@router.get("/", response_model=List[ProjectDocumentSchema])
async def get_documents(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    project_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    uploader_id: Optional[int] = Query(None, description="Filtrar por subidor"),
    file_type: Optional[str] = Query(None, description="Filtrar por tipo de archivo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de documentos"""
    
    query = db.query(ProjectDocument)
    
    # Aplicar filtros de búsqueda
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (ProjectDocument.name.ilike(search_term)) |
            (ProjectDocument.description.ilike(search_term))
        )
    
    if project_id:
        query = query.filter(ProjectDocument.project_id == project_id)
    
    if uploader_id:
        query = query.filter(ProjectDocument.uploader_id == uploader_id)
    
    if file_type:
        query = query.filter(ProjectDocument.file_type == file_type)
    
    # Aplicar paginación
    documents = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for document in documents:
        # Obtener nombre del subidor
        uploader = db.query(User).filter(User.id == document.uploader_id).first()
        uploader_name = uploader.full_name if uploader else "Desconocido"
        
        # Obtener nombre del proyecto
        project = db.query(Project).filter(Project.id == document.project_id).first()
        project_name = project.name if project else "Desconocido"
        
        document_data = ProjectDocumentSchema(
            **document.__dict__,
            uploader_name=uploader_name,
            project_name=project_name
        )
        result.append(document_data)
    
    return result

@router.get("/project/{project_id}", response_model=List[ProjectDocumentSchema])
async def get_project_documents(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener documentos de un proyecto específico"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    documents = db.query(ProjectDocument).filter(
        ProjectDocument.project_id == project_id
    ).offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for document in documents:
        # Obtener nombre del subidor
        uploader = db.query(User).filter(User.id == document.uploader_id).first()
        uploader_name = uploader.full_name if uploader else "Desconocido"
        
        # Crear el schema con los datos del documento
        document_data = ProjectDocumentSchema(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            file_path=document.file_path,
            file_type=document.file_type,
            file_size=document.file_size,
            project_id=document.project_id,
            uploader_id=document.uploader_id,
            description=document.description,
            created_at=document.created_at,
            updated_at=document.updated_at,
            uploader_name=uploader_name,
            project_name=project.name
        )
        result.append(document_data)
    
    return result

@router.get("/{document_id}", response_model=ProjectDocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener documento por ID"""
    
    document = db.query(ProjectDocument).filter(ProjectDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Obtener nombre del subidor
    uploader = db.query(User).filter(User.id == document.uploader_id).first()
    uploader_name = uploader.full_name if uploader else "Desconocido"
    
    # Obtener nombre del proyecto
    project = db.query(Project).filter(Project.id == document.project_id).first()
    project_name = project.name if project else "Desconocido"
    
    return ProjectDocumentSchema(
        **document.__dict__,
        uploader_name=uploader_name,
        project_name=project_name
    )

@router.post("/upload", response_model=ProjectDocumentSchema, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir nuevo documento"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede subir documentos
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir documentos a este proyecto"
        )
    
    # Validar archivo
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo no válido"
        )
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Verificar tamaño del archivo
    file_size = 0
    file_content = b""
    
    # Leer archivo en chunks para verificar tamaño
    chunk_size = 1024 * 1024  # 1MB chunks
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_size += len(chunk)
        file_content += chunk
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / (1024*1024)} MB"
            )
    
    # Generar nombre único para el archivo
    unique_filename = generate_unique_filename(file.filename)
    
    # Crear directorio del proyecto si no existe
    project_upload_dir = os.path.join(settings.UPLOAD_DIR, str(project_id))
    os.makedirs(project_upload_dir, exist_ok=True)
    
    # Guardar archivo
    file_path = os.path.join(project_upload_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # Crear registro en base de datos
    db_document = ProjectDocument(
        filename=name,
        original_filename=file.filename,
        file_path=file_path,
        file_type=get_file_extension(file.filename),
        file_size=file_size,
        description=description,
        project_id=project_id,
        uploader_id=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="upload_document",
        entity_type="document",
        entity_id=str(db_document.id),
        details=f"Documento subido: {name} ({get_file_size_mb(file_size)} MB) al proyecto {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_document

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Descargar documento"""
    
    document = db.query(ProjectDocument).filter(ProjectDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar que el archivo existe físicamente
    # Si la ruta no es absoluta, buscar en el directorio backend
    if not os.path.isabs(document.file_path):
        # Buscar en el directorio backend
        backend_file_path = os.path.join("backend", document.file_path)
        if os.path.exists(backend_file_path):
            document.file_path = backend_file_path
        elif not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado en el servidor"
            )
    
    # Registrar descarga en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="download_document",
        entity_type="document",
        entity_id=str(document_id),
        details=f"Documento descargado: {document.filename}"
    )
    db.add(audit_log)
    db.commit()
    
    # Determinar el tipo MIME basado en la extensión del archivo
    def get_mime_type(filename: str) -> str:
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        return mime_types.get(ext, 'application/octet-stream')
    
    # Retornar archivo para descarga con headers CORS
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename or document.filename,
        media_type=get_mime_type(document.original_filename or document.filename),
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Authorization, Content-Type',
            'Content-Disposition': f'attachment; filename="{document.original_filename or document.filename}"'
        }
    )

@router.put("/{document_id}", response_model=ProjectDocumentSchema)
async def update_document(
    document_id: int,
    document_data: ProjectDocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar documento"""
    
    # Verificar que el documento existe
    document = db.query(ProjectDocument).filter(ProjectDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos: solo el subidor, propietario del proyecto o admin puede actualizar
    project = db.query(Project).filter(Project.id == document.project_id).first()
    if (document.uploader_id != current_user.id and 
        project.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este documento"
        )
    
    # Actualizar campos
    update_data = document_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_document",
        entity_type="document",
        entity_id=str(document_id),
        details=f"Documento actualizado: {document.original_filename or document.filename}"
    )
    db.add(audit_log)
    db.commit()
    
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar documento"""
    
    # Verificar que el documento existe
    document = db.query(ProjectDocument).filter(ProjectDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    # Verificar permisos: solo el subidor, propietario del proyecto o admin puede eliminar
    project = db.query(Project).filter(Project.id == document.project_id).first()
    if (document.uploader_id != current_user.id and 
        project.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este documento"
        )
    
    # Eliminar archivo físico si existe
    file_path_to_delete = document.file_path
    
    # Si la ruta no es absoluta, buscar en el directorio backend
    if not os.path.isabs(file_path_to_delete):
        backend_file_path = os.path.join("backend", file_path_to_delete)
        if os.path.exists(backend_file_path):
            file_path_to_delete = backend_file_path
        elif os.path.exists(file_path_to_delete):
            file_path_to_delete = file_path_to_delete
        else:
            file_path_to_delete = None
    
    # Eliminar archivo si existe
    if file_path_to_delete and os.path.exists(file_path_to_delete):
        try:
            os.remove(file_path_to_delete)
            print(f"Archivo eliminado exitosamente: {file_path_to_delete}")
        except OSError as e:
            # Log error pero continuar con la eliminación del registro
            print(f"Error eliminando archivo físico {file_path_to_delete}: {e}")
    else:
        print(f"Archivo no encontrado para eliminar: {document.file_path}")
    
    # Eliminar registro de base de datos
    db.delete(document)
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_document",
        entity_type="document",
        entity_id=str(document_id),
        details=f"Documento eliminado: {document.original_filename or document.filename}"
    )
    db.add(audit_log)
    db.commit()
    
    return None

@router.get("/stats/summary")
async def get_documents_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas resumidas de documentos"""
    
    total_documents = db.query(ProjectDocument).count()
    total_size_bytes = db.query(ProjectDocument.file_size).all()
    total_size_mb = sum(size[0] for size in total_size_bytes) / (1024 * 1024)
    
    # Documentos del usuario actual
    my_documents = db.query(ProjectDocument).filter(ProjectDocument.uploader_id == current_user.id).count()
    my_size_bytes = db.query(ProjectDocument.file_size).filter(
        ProjectDocument.uploader_id == current_user.id
    ).all()
    my_size_mb = sum(size[0] for size in my_size_bytes) / (1024 * 1024)
    
    # Contar por tipo de archivo
    file_types = db.query(ProjectDocument.file_type).distinct().all()
    type_counts = {}
    for file_type in file_types:
        count = db.query(ProjectDocument).filter(ProjectDocument.file_type == file_type[0]).count()
        type_counts[file_type[0]] = count
    
    return {
        "total_documents": total_documents,
        "total_size_mb": round(total_size_mb, 2),
        "my_documents": my_documents,
        "my_size_mb": round(my_size_mb, 2),
        "file_types": type_counts
    }

@router.get("/file-types")
async def get_supported_file_types(
    current_user: User = Depends(get_current_user)
):
    """Obtener tipos de archivo soportados"""
    
    return {
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
    }

