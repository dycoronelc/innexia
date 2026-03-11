from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os
import shutil
from datetime import datetime

from ..core.auth import get_current_user, get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..models.activity import ProjectActivity, ActivityAssignee, ActivityTag, ActivityLabel
from ..models.activity_comment import ActivityComment
from ..models.activity_checklist import ActivityChecklist, ActivityChecklistItem
from ..models.activity_attachment import ActivityAttachment
from ..models.tag import Tag
from ..models.category import Category

router = APIRouter()

# ============================================================================
# ASIGNADOS MÚLTIPLES
# ============================================================================

@router.post("/{activity_id}/assignees")
async def add_assignee_to_activity(
    activity_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar un asignado a una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que no esté ya asignado
    existing_assignee = db.query(ActivityAssignee).filter(
        and_(
            ActivityAssignee.activity_id == activity_id,
            ActivityAssignee.user_id == user_id
        )
    ).first()
    
    if existing_assignee:
        raise HTTPException(status_code=400, detail="El usuario ya está asignado a esta actividad")
    
    # Crear nuevo asignado
    assignee = ActivityAssignee(
        activity_id=activity_id,
        user_id=user_id
    )
    db.add(assignee)
    db.commit()
    
    return {"message": "Asignado agregado exitosamente"}

@router.delete("/{activity_id}/assignees/{user_id}")
async def remove_assignee_from_activity(
    activity_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remover un asignado de una actividad"""
    
    assignee = db.query(ActivityAssignee).filter(
        and_(
            ActivityAssignee.activity_id == activity_id,
            ActivityAssignee.user_id == user_id
        )
    ).first()
    
    if not assignee:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    db.delete(assignee)
    db.commit()
    
    return {"message": "Asignado removido exitosamente"}

@router.get("/{activity_id}/assignees")
async def get_activity_assignees(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los asignados de una actividad"""
    
    assignees = db.query(ActivityAssignee).filter(
        ActivityAssignee.activity_id == activity_id
    ).all()
    
    result = []
    for assignee in assignees:
        user = db.query(User).filter(User.id == assignee.user_id).first()
        if user:
            result.append({
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "assigned_at": assignee.assigned_at
            })
    
    return result

# ============================================================================
# ETIQUETAS (TAGS)
# ============================================================================

@router.post("/{activity_id}/tags")
async def add_tag_to_activity(
    activity_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar una etiqueta a una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Verificar que la etiqueta existe
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    
    # Verificar que no esté ya agregada
    existing_tag = db.query(ActivityTag).filter(
        and_(
            ActivityTag.activity_id == activity_id,
            ActivityTag.tag_id == tag_id
        )
    ).first()
    
    if existing_tag:
        raise HTTPException(status_code=400, detail="La etiqueta ya está agregada a esta actividad")
    
    # Crear nueva etiqueta
    activity_tag = ActivityTag(
        activity_id=activity_id,
        tag_id=tag_id
    )
    db.add(activity_tag)
    db.commit()
    
    return {"message": "Etiqueta agregada exitosamente"}

@router.delete("/{activity_id}/tags/{tag_id}")
async def remove_tag_from_activity(
    activity_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remover una etiqueta de una actividad"""
    
    activity_tag = db.query(ActivityTag).filter(
        and_(
            ActivityTag.activity_id == activity_id,
            ActivityTag.tag_id == tag_id
        )
    ).first()
    
    if not activity_tag:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    
    db.delete(activity_tag)
    db.commit()
    
    return {"message": "Etiqueta removida exitosamente"}

@router.get("/{activity_id}/tags")
async def get_activity_tags(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las etiquetas de una actividad"""
    
    activity_tags = db.query(ActivityTag).filter(
        ActivityTag.activity_id == activity_id
    ).all()
    
    result = []
    for activity_tag in activity_tags:
        tag = db.query(Tag).filter(Tag.id == activity_tag.tag_id).first()
        if tag:
            result.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color,
                "created_at": activity_tag.created_at
            })
    
    return result

# ============================================================================
# ETIQUETAS DE COLOR (LABELS)
# ============================================================================

@router.post("/{activity_id}/labels")
async def add_label_to_activity(
    activity_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar una etiqueta de color a una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Verificar que la categoría existe
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar que no esté ya agregada
    existing_label = db.query(ActivityLabel).filter(
        and_(
            ActivityLabel.activity_id == activity_id,
            ActivityLabel.category_id == category_id
        )
    ).first()
    
    if existing_label:
        raise HTTPException(status_code=400, detail="La etiqueta de color ya está agregada a esta actividad")
    
    # Crear nueva etiqueta de color
    label = ActivityLabel(
        activity_id=activity_id,
        category_id=category_id
    )
    db.add(label)
    db.commit()
    
    return {"message": "Etiqueta de color agregada exitosamente"}

@router.delete("/{activity_id}/labels/{category_id}")
async def remove_label_from_activity(
    activity_id: int,
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remover una etiqueta de color de una actividad"""
    
    label = db.query(ActivityLabel).filter(
        and_(
            ActivityLabel.activity_id == activity_id,
            ActivityLabel.category_id == category_id
        )
    ).first()
    
    if not label:
        raise HTTPException(status_code=404, detail="Etiqueta de color no encontrada")
    
    db.delete(label)
    db.commit()
    
    return {"message": "Etiqueta de color removida exitosamente"}

@router.get("/{activity_id}/labels")
async def get_activity_labels(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las etiquetas de color de una actividad"""
    
    labels = db.query(ActivityLabel).filter(
        ActivityLabel.activity_id == activity_id
    ).all()
    
    result = []
    for label in labels:
        category = db.query(Category).filter(Category.id == label.category_id).first()
        if category:
            result.append({
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "created_at": label.created_at
            })
    
    return result

# ============================================================================
# COMENTARIOS
# ============================================================================

@router.post("/{activity_id}/comments")
async def add_comment_to_activity(
    activity_id: int,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar un comentario a una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Crear nuevo comentario
    comment = ActivityComment(
        activity_id=activity_id,
        author_id=current_user.id,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "content": comment.content,
        "author_id": comment.author_id,
        "author_name": current_user.full_name,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    }

@router.get("/{activity_id}/comments")
async def get_activity_comments(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los comentarios de una actividad"""
    
    comments = db.query(ActivityComment).filter(
        ActivityComment.activity_id == activity_id
    ).order_by(ActivityComment.created_at.desc()).all()
    
    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.author_id).first()
        result.append({
            "id": comment.id,
            "content": comment.content,
            "author_id": comment.author_id,
            "author_name": author.full_name if author else "Usuario desconocido",
            "created_at": comment.created_at,
            "updated_at": comment.updated_at
        })
    
    return result

@router.delete("/{activity_id}/comments/{comment_id}")
async def delete_activity_comment(
    activity_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un comentario de una actividad"""
    
    comment = db.query(ActivityComment).filter(
        and_(
            ActivityComment.id == comment_id,
            ActivityComment.activity_id == activity_id
        )
    ).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    
    # Solo el autor puede eliminar su comentario
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este comentario")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comentario eliminado exitosamente"}

# ============================================================================
# CHECKLISTS
# ============================================================================

@router.post("/{activity_id}/checklists")
async def create_checklist(
    activity_id: int,
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un checklist para una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Crear nuevo checklist
    checklist = ActivityChecklist(
        activity_id=activity_id,
        title=title
    )
    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    
    return {
        "id": checklist.id,
        "title": checklist.title,
        "activity_id": checklist.activity_id,
        "created_at": checklist.created_at,
        "updated_at": checklist.updated_at,
        "items": []
    }

@router.get("/{activity_id}/checklists")
async def get_activity_checklists(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los checklists de una actividad"""
    
    checklists = db.query(ActivityChecklist).filter(
        ActivityChecklist.activity_id == activity_id
    ).all()
    
    result = []
    for checklist in checklists:
        items = db.query(ActivityChecklistItem).filter(
            ActivityChecklistItem.checklist_id == checklist.id
        ).all()
        
        items_data = []
        for item in items:
            completed_by = None
            if item.completed_by_id:
                user = db.query(User).filter(User.id == item.completed_by_id).first()
                completed_by = user.full_name if user else "Usuario desconocido"
            
            items_data.append({
                "id": item.id,
                "content": item.content,
                "completed": item.completed,
                "completed_at": item.completed_at,
                "completed_by": completed_by,
                "created_at": item.created_at
            })
        
        result.append({
            "id": checklist.id,
            "title": checklist.title,
            "activity_id": checklist.activity_id,
            "created_at": checklist.created_at,
            "updated_at": checklist.updated_at,
            "items": items_data
        })
    
    return result

@router.post("/checklists/{checklist_id}/items")
async def add_checklist_item(
    checklist_id: int,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Agregar un item a un checklist"""
    
    # Verificar que el checklist existe
    checklist = db.query(ActivityChecklist).filter(ActivityChecklist.id == checklist_id).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist no encontrado")
    
    # Crear nuevo item
    item = ActivityChecklistItem(
        checklist_id=checklist_id,
        content=content,
        completed=False
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return {
        "id": item.id,
        "content": item.content,
        "completed": item.completed,
        "completed_at": item.completed_at,
        "completed_by": None,
        "created_at": item.created_at
    }

@router.put("/checklist-items/{item_id}/toggle")
async def toggle_checklist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar el estado de completado de un item del checklist"""
    
    item = db.query(ActivityChecklistItem).filter(ActivityChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    item.completed = not item.completed
    if item.completed:
        item.completed_at = datetime.utcnow()
        item.completed_by_id = current_user.id
    else:
        item.completed_at = None
        item.completed_by_id = None
    
    db.commit()
    db.refresh(item)
    
    completed_by = None
    if item.completed_by_id:
        user = db.query(User).filter(User.id == item.completed_by_id).first()
        completed_by = user.full_name if user else "Usuario desconocido"
    
    return {
        "id": item.id,
        "content": item.content,
        "completed": item.completed,
        "completed_at": item.completed_at,
        "completed_by": completed_by,
        "created_at": item.created_at
    }

@router.delete("/checklist-items/{item_id}")
async def delete_checklist_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un item del checklist"""
    
    item = db.query(ActivityChecklistItem).filter(ActivityChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    db.delete(item)
    db.commit()
    
    return {"message": "Item eliminado exitosamente"}

# ============================================================================
# ADJUNTOS
# ============================================================================

@router.post("/{activity_id}/attachments")
async def upload_attachment(
    activity_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir un adjunto a una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    
    # Crear directorio si no existe
    upload_dir = f"uploads/activities/{activity_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generar nombre único para el archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Guardar archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Obtener tamaño del archivo
    file_size = os.path.getsize(file_path)
    
    # Crear registro en la base de datos
    attachment = ActivityAttachment(
        activity_id=activity_id,
        name=filename,
        original_name=file.filename,
        file_path=file_path,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        description=description,
        uploader_id=current_user.id
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return {
        "id": attachment.id,
        "name": attachment.name,
        "original_name": attachment.original_name,
        "file_type": attachment.file_type,
        "file_size": attachment.file_size,
        "description": attachment.description,
        "uploader_id": attachment.uploader_id,
        "uploader_name": current_user.full_name,
        "created_at": attachment.created_at,
        "updated_at": attachment.updated_at
    }

@router.get("/{activity_id}/attachments")
async def get_activity_attachments(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los adjuntos de una actividad"""
    
    attachments = db.query(ActivityAttachment).filter(
        ActivityAttachment.activity_id == activity_id
    ).all()
    
    result = []
    for attachment in attachments:
        uploader = db.query(User).filter(User.id == attachment.uploader_id).first()
        result.append({
            "id": attachment.id,
            "name": attachment.name,
            "original_name": attachment.original_name,
            "file_type": attachment.file_type,
            "file_size": attachment.file_size,
            "description": attachment.description,
            "uploader_id": attachment.uploader_id,
            "uploader_name": uploader.full_name if uploader else "Usuario desconocido",
            "created_at": attachment.created_at,
            "updated_at": attachment.updated_at
        })
    
    return result

@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar un adjunto"""
    
    attachment = db.query(ActivityAttachment).filter(ActivityAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    
    # Solo el subidor puede eliminar el archivo
    if attachment.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este adjunto")
    
    # Eliminar archivo físico
    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
    
    # Eliminar registro de la base de datos
    db.delete(attachment)
    db.commit()
    
    return {"message": "Adjunto eliminado exitosamente"}
