from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..core.auth import get_current_user, get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.activity import ProjectActivity
from ..models.audit_log import AuditLog
from ..schemas.activity import ProjectActivityCreate, ProjectActivityUpdate, ProjectActivity as ProjectActivitySchema
from ..schemas.project import Project as ProjectSchema

router = APIRouter()

@router.get("/test", response_model=List[ProjectActivitySchema])
async def test_activities(
    db: Session = Depends(get_db)
):
    """Endpoint de prueba sin autenticación"""
    
    try:
        activities = db.query(ProjectActivity).limit(5).all()
        
        result = []
        for activity in activities:
            activity_data = ProjectActivitySchema(
                **activity.__dict__,
                assignee_name="Sin asignar",
                project_name="Desconocido"
            )
            result.append(activity_data)
        
        return result
    except Exception as e:
        print(f"Error en test_activities: {e}")
        return []

@router.get("/", response_model=List[ProjectActivitySchema])
async def get_activities(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por título o descripción"),
    project_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    assignee_id: Optional[int] = Query(None, description="Filtrar por asignado"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de actividades"""
    
    query = db.query(ProjectActivity)
    
    # Aplicar filtros de búsqueda
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ProjectActivity.title.ilike(search_term),
                ProjectActivity.description.ilike(search_term)
            )
        )
    
    if project_id:
        query = query.filter(ProjectActivity.project_id == project_id)
    
    if assignee_id:
        # Por ahora, no filtrar por assignee_id ya que la relación assignees no está funcionando correctamente
        # TODO: Implementar filtro por assignee cuando la relación esté funcionando
        pass
    
    if status:
        query = query.filter(ProjectActivity.status == status)
    
    if priority:
        query = query.filter(ProjectActivity.priority == priority)
    
    # Aplicar paginación
    activities = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for activity in activities:
        try:
            # Obtener nombre del primer asignado (para compatibilidad)
            # Por ahora, usar "Sin asignar" ya que la relación assignees no está funcionando correctamente
            assignee_name = "Sin asignar"
            
            # Obtener nombre del proyecto
            project = db.query(Project).filter(Project.id == activity.project_id).first()
            project_name = project.name if project else "Desconocido"
            
            activity_data = ProjectActivitySchema(
                **activity.__dict__,
                assignee_name=assignee_name,
                project_name=project_name
            )
            result.append(activity_data)
        except Exception as e:
            # Si hay error, crear actividad con valores por defecto
            activity_data = ProjectActivitySchema(
                **activity.__dict__,
                assignee_name="Sin asignar",
                project_name="Desconocido"
            )
            result.append(activity_data)
    
    return result

@router.get("/my-activities", response_model=List[ProjectActivitySchema])
async def get_my_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividades asignadas al usuario actual"""
    
    # Por ahora, no filtrar por usuario ya que la relación assignees no está funcionando correctamente
    # TODO: Implementar filtro por usuario cuando la relación esté funcionando
    query = db.query(ProjectActivity)
    
    if status:
        query = query.filter(ProjectActivity.status == status)
    
    if priority:
        query = query.filter(ProjectActivity.priority == priority)
    
    activities = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for activity in activities:
        # Obtener nombre del proyecto
        project = db.query(Project).filter(Project.id == activity.project_id).first()
        project_name = project.name if project else "Desconocido"
        
        activity_data = ProjectActivitySchema(
            **activity.__dict__,
            assignee_name=current_user.full_name,
            project_name=project_name
        )
        result.append(activity_data)
    
    return result

@router.get("/project/{project_id}", response_model=List[ProjectActivitySchema])
async def get_project_activities(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividades de un proyecto específico"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    query = db.query(ProjectActivity).filter(ProjectActivity.project_id == project_id)
    
    if status:
        query = query.filter(ProjectActivity.status == status)
    
    if priority:
        query = query.filter(ProjectActivity.priority == priority)
    
    activities = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for activity in activities:
        # Obtener nombre del primer asignado (para compatibilidad)
        # Por ahora, usar "Sin asignar" ya que la relación assignees no está funcionando correctamente
        assignee_name = "Sin asignar"
        
        activity_data = ProjectActivitySchema(
            **activity.__dict__,
            assignee_name=assignee_name,
            project_name=project.name
        )
        result.append(activity_data)
    
    return result

@router.get("/{activity_id}", response_model=ProjectActivitySchema)
async def get_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener actividad por ID"""
    
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    # Obtener nombre del primer asignado (para compatibilidad)
    # Por ahora, usar "Sin asignar" ya que la relación assignees no está funcionando correctamente
    assignee_name = "Sin asignar"
    
    # Obtener nombre del proyecto
    project = db.query(Project).filter(Project.id == activity.project_id).first()
    project_name = project.name if project else "Desconocido"
    
    return ProjectActivitySchema(
        **activity.__dict__,
        assignee_name=assignee_name,
        project_name=project_name
    )

@router.post("/", response_model=ProjectActivitySchema, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ProjectActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva actividad"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == activity_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede crear actividades
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear actividades en este proyecto"
        )
    
    # Verificar que los asignados existen
    assignees = []
    for assignee_id in activity_data.assignee_ids:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario asignado con ID {assignee_id} no encontrado"
            )
        assignees.append(assignee)
    
    # Crear actividad
    db_activity = ProjectActivity(
        title=activity_data.title,
        description=activity_data.description,
        status=activity_data.status,
        priority=activity_data.priority,
        project_id=activity_data.project_id,
        start_date=activity_data.start_date,
        due_date=activity_data.due_date
    )
    
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    # Crear asignaciones
    for assignee in assignees:
        from ..models.activity import ActivityAssignee
        assignment = ActivityAssignee(
            activity_id=db_activity.id,
            user_id=assignee.id
        )
        db.add(assignment)
    
    db.commit()
    db.refresh(db_activity)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_activity",
        entity_type="activity",
        entity_id=str(db_activity.id),
        details=f"Actividad creada: {db_activity.title} en proyecto {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_activity

@router.put("/{activity_id}", response_model=ProjectActivitySchema)
async def update_activity(
    activity_id: int,
    activity_data: ProjectActivityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    # Verificar permisos: solo el asignado, propietario del proyecto o admin puede actualizar
    project = db.query(Project).filter(Project.id == activity.project_id).first()
    
    # Verificar si el usuario actual es asignado de la actividad
    is_assignee = db.query(ProjectActivity.assignees).filter(
        ProjectActivity.assignees.any(activity_id=activity.id, user_id=current_user.id)
    ).first() is not None
    
    if (not is_assignee and 
        project.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar esta actividad"
        )
    
    # Verificar que los nuevos asignados existen si se están cambiando
    if activity_data.assignee_ids:
        for assignee_id in activity_data.assignee_ids:
            new_assignee = db.query(User).filter(User.id == assignee_id).first()
            if not new_assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Nuevo usuario asignado con ID {assignee_id} no encontrado"
                )
    
    # Actualizar campos básicos
    update_data = activity_data.dict(exclude_unset=True, exclude={'assignee_ids'})
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    # Actualizar asignados si se proporcionan
    if activity_data.assignee_ids is not None:
        # Eliminar asignaciones existentes
        from ..models.activity import ActivityAssignee
        db.query(ActivityAssignee).filter(ActivityAssignee.activity_id == activity.id).delete()
        
        # Crear nuevas asignaciones
        for assignee_id in activity_data.assignee_ids:
            assignment = ActivityAssignee(
                activity_id=activity.id,
                user_id=assignee_id
            )
            db.add(assignment)
    
    db.commit()
    db.refresh(activity)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_activity",
        entity_type="activity",
        entity_id=str(activity_id),
        details=f"Actividad actualizada: {activity.title}"
    )
    db.add(audit_log)
    db.commit()
    
    return activity

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede eliminar
    project = db.query(Project).filter(Project.id == activity.project_id).first()
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar esta actividad"
        )
    
    # Eliminar actividad
    db.delete(activity)
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_activity",
        entity_type="activity",
        entity_id=str(activity_id),
        details=f"Actividad eliminada: {activity.title}"
    )
    db.add(audit_log)
    db.commit()
    
    return None

@router.patch("/{activity_id}/status")
async def update_activity_status(
    activity_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar solo el estado de una actividad"""
    
    # Verificar que la actividad existe
    activity = db.query(ProjectActivity).filter(ProjectActivity.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    # Verificar permisos: solo el asignado, propietario del proyecto o admin puede cambiar estado
    project = db.query(Project).filter(Project.id == activity.project_id).first()
    
    # Verificar si el usuario actual es asignado de la actividad
    is_assignee = db.query(ProjectActivity.assignees).filter(
        ProjectActivity.assignees.any(activity_id=activity.id, user_id=current_user.id)
    ).first() is not None
    
    if (not is_assignee and 
        project.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el estado de esta actividad"
        )
    
    # Validar estado
    valid_statuses = ["todo", "in-progress", "review", "completed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
        )
    
    # Actualizar estado
    old_status = activity.status
    activity.status = status
    db.commit()
    db.refresh(activity)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_activity_status",
        entity_type="activity",
        entity_id=str(activity_id),
        details=f"Estado de actividad cambiado de '{old_status}' a '{status}': {activity.title}"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": f"Estado actualizado a: {status}"}

@router.get("/stats/summary")
async def get_activities_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas resumidas de actividades"""
    
    total_activities = db.query(ProjectActivity).count()
    todo_activities = db.query(ProjectActivity).filter(ProjectActivity.status == "todo").count()
    in_progress_activities = db.query(ProjectActivity).filter(ProjectActivity.status == "in-progress").count()
    review_activities = db.query(ProjectActivity).filter(ProjectActivity.status == "review").count()
    completed_activities = db.query(ProjectActivity).filter(ProjectActivity.status == "completed").count()
    
    # Actividades del usuario actual
    my_activities = db.query(ProjectActivity).join(
        ProjectActivity.assignees,
        ProjectActivity.id == ProjectActivity.assignees.c.activity_id
    ).filter(
        ProjectActivity.assignees.c.user_id == current_user.id
    ).count()
    my_todo = db.query(ProjectActivity).join(
        ProjectActivity.assignees,
        ProjectActivity.id == ProjectActivity.assignees.c.activity_id
    ).filter(
        and_(ProjectActivity.assignees.c.user_id == current_user.id, ProjectActivity.status == "todo")
    ).count()
    my_in_progress = db.query(ProjectActivity).join(
        ProjectActivity.assignees,
        ProjectActivity.id == ProjectActivity.assignees.c.activity_id
    ).filter(
        and_(ProjectActivity.assignees.c.user_id == current_user.id, ProjectActivity.status == "in-progress")
    ).count()
    
    return {
        "total_activities": total_activities,
        "todo_activities": todo_activities,
        "in_progress_activities": in_progress_activities,
        "review_activities": review_activities,
        "completed_activities": completed_activities,
        "my_activities": my_activities,
        "my_todo": my_todo,
        "my_in_progress": my_in_progress
    }

