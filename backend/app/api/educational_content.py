from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from PIL import Image
import io
from app.database import get_db
from app.core.auth import get_current_user
from app.schemas.educational_content import (
    EducationalContentCreate,
    EducationalContentUpdate,
    EducationalContentResponse,
    EducationalContentList,
    EducationalContentFilters
)
from app.models.educational_content import EducationalContent, ContentStatus
from app.models.user import User
from sqlalchemy import func

router = APIRouter()

@router.get("/", response_model=List[EducationalContentList])
async def get_educational_content(
    search: Optional[str] = Query(None, description="Término de búsqueda"),
    content_type: Optional[str] = Query(None, description="Tipo de contenido"),
    difficulty: Optional[str] = Query(None, description="Nivel de dificultad"),
    status: Optional[str] = Query(None, description="Estado del contenido"),
    author: Optional[str] = Query(None, description="Autor del contenido"),
    limit: int = Query(20, ge=1, le=100, description="Número de elementos por página"),
    offset: int = Query(0, ge=0, description="Número de elementos a saltar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista de contenido educativo con filtros opcionales
    """
    query = db.query(EducationalContent)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            EducationalContent.title.ilike(f"%{search}%") |
            EducationalContent.description.ilike(f"%{search}%")
        )
    
    if content_type:
        query = query.filter(EducationalContent.content_type == content_type)
    
    if difficulty:
        query = query.filter(EducationalContent.difficulty == difficulty)
    
    if status:
        query = query.filter(EducationalContent.status == status)
    
    if author:
        query = query.filter(EducationalContent.author.ilike(f"%{author}%"))
    
    # Solo mostrar contenido publicado para usuarios normales
    if current_user.role != "admin":
        query = query.filter(EducationalContent.status == ContentStatus.PUBLISHED)
    
    # Aplicar paginación
    total = query.count()
    content = query.offset(offset).limit(limit).all()
    
    return content

@router.post("/", response_model=EducationalContentResponse, status_code=status.HTTP_201_CREATED)
async def create_educational_content(
    content_data: EducationalContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear nuevo contenido educativo
    """
    # Verificar permisos
    if current_user.role not in ["admin", "content_creator", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear contenido educativo"
        )
    
    # Crear el contenido
    content_dict = content_data.dict()
    status = content_dict.pop('status', ContentStatus.DRAFT)
    
    db_content = EducationalContent(
        **content_dict,
        created_by=current_user.id,
        status=status
    )
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return db_content

@router.get("/{content_id}", response_model=EducationalContentResponse)
async def get_educational_content_by_id(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener contenido educativo específico por ID
    """
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contenido educativo no encontrado"
        )
    
    # Verificar acceso
    if content.status != ContentStatus.PUBLISHED and current_user.role not in ["admin", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este contenido"
        )
    
    # Incrementar contador de vistas
    content.view_count += 1
    db.commit()
    
    return content

@router.put("/{content_id}", response_model=EducationalContentResponse)
async def update_educational_content(
    content_id: int,
    content_data: EducationalContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar contenido educativo existente
    """
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contenido educativo no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "content_editor"] and content.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este contenido"
        )
    
    # Actualizar campos
    update_data = content_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    content.updated_at = func.now()
    db.commit()
    db.refresh(content)
    
    return content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_educational_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar contenido educativo
    """
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contenido educativo no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar contenido educativo"
        )
    
    db.delete(content)
    db.commit()
    
    return None

@router.post("/{content_id}/publish", response_model=EducationalContentResponse)
async def publish_educational_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Publicar contenido educativo
    """
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contenido educativo no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "content_editor", "content_moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para publicar contenido"
        )
    
    # Cambiar estado a publicado
    content.status = ContentStatus.PUBLISHED
    content.published_at = func.now()
    content.moderated_by = current_user.id
    
    db.commit()
    db.refresh(content)
    
    return content

@router.post("/{content_id}/archive", response_model=EducationalContentResponse)
async def archive_educational_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archivar contenido educativo
    """
    content = db.query(EducationalContent).filter(EducationalContent.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contenido educativo no encontrado"
        )
    
    # Verificar permisos
    if current_user.role not in ["admin", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para archivar contenido"
        )
    
    # Cambiar estado a archivado
    content.status = ContentStatus.ARCHIVED
    
    db.commit()
    db.refresh(content)
    
    return content

@router.post("/upload-file")
async def upload_content_file(
    file: UploadFile = File(...),
    content_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subir archivo de contenido educativo
    """
    # Verificar permisos
    if current_user.role not in ["admin", "content_creator", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir archivos de contenido"
        )
    
    # Validar tipo de archivo
    allowed_extensions = {
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.aac'],
        'document': ['.pdf', '.doc', '.docx', '.ppt', '.pptx'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    }
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if content_type not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de contenido no válido: {content_type}"
        )
    
    if file_extension not in allowed_extensions[content_type]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de archivo no válida para {content_type}: {file_extension}"
        )
    
    # Crear directorio de uploads si no existe
    upload_dir = "uploads/educational_content"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único para el archivo
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Generar URL del archivo
        file_url = f"/uploads/educational_content/{filename}"
        
        return {
            "status": "success",
            "message": "Archivo subido exitosamente",
            "data": {
                "filename": filename,
                "url": file_url,
                "size": len(content),
                "content_type": content_type,
                "original_filename": file.filename
            }
        }
        
    except Exception as e:
        # Eliminar archivo si hay error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivo: {str(e)}"
        )

@router.post("/upload-thumbnail")
async def upload_thumbnail(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subir imagen miniatura con redimensionamiento automático
    """
    # Verificar permisos
    if current_user.role not in ["admin", "content_creator", "content_editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para subir imágenes"
        )
    
    # Validar que sea una imagen
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen"
        )
    
    # Validar extensiones de imagen
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de imagen no válida: {file_extension}. Extensiones permitidas: {', '.join(allowed_extensions)}"
        )
    
    # Crear directorio de thumbnails si no existe
    thumbnail_dir = "uploads/educational_content/thumbnails"
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    try:
        # Leer la imagen
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir a RGB si es necesario (para manejar PNG con transparencia)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Redimensionar a tamaño óptimo (400x225 para ratio 16:9)
        optimal_size = (400, 225)
        image_resized = image.resize(optimal_size, Image.Resampling.LANCZOS)
        
        # Generar nombre único para el archivo
        file_id = str(uuid.uuid4())
        filename = f"thumb_{file_id}.jpg"
        file_path = os.path.join(thumbnail_dir, filename)
        
        # Guardar imagen redimensionada
        image_resized.save(file_path, 'JPEG', quality=85, optimize=True)
        
        # Generar URL del archivo
        file_url = f"/uploads/educational_content/thumbnails/{filename}"
        
        # Obtener información del archivo
        file_size = os.path.getsize(file_path)
        
        return {
            "status": "success",
            "message": "Miniatura subida y redimensionada exitosamente",
            "data": {
                "filename": filename,
                "url": file_url,
                "size": file_size,
                "original_size": image.size,
                "resized_size": optimal_size,
                "format": "JPEG"
            }
        }
        
    except Exception as e:
        # Eliminar archivo si hay error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar imagen: {str(e)}"
        )
