from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..core.auth import get_current_user, get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project, ProjectTag
from ..models.audit_log import AuditLog
from ..models.category import Category
from ..models.location import Location
from ..models.status import Status
from ..models.tag import Tag
from ..schemas.project import ProjectCreate, ProjectUpdate, Project as ProjectSchema, ProjectWithDetails
from ..schemas.user import User as UserSchema

router = APIRouter()

@router.get("/", response_model=List[ProjectWithDetails])
async def get_projects(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nombre o descripción"),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    location: Optional[str] = Query(None, description="Filtrar por ubicación"),
    status: Optional[str] = Query(None, description="Filtrar por estado"),
    owner_id: Optional[int] = Query(None, description="Filtrar por propietario"),
    tags: Optional[str] = Query(None, description="Filtrar por etiquetas (separadas por coma)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de proyectos"""
    
    # Filtrar solo proyectos de la empresa del usuario actual
    query = db.query(Project).filter(Project.company_id == current_user.company_id)
    
    # Aplicar filtros de búsqueda
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term)
            )
        )
    
    if category:
        query = query.filter(Project.category == category)
    
    if location:
        query = query.filter(Project.location == location)
    
    if status:
        query = query.filter(Project.status == status)
    
    if owner_id:
        query = query.filter(Project.owner_id == owner_id)
    
    # Filtrar por etiquetas
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.join(ProjectTag).filter(ProjectTag.tag_name == tag)
    
    # Aplicar paginación
    projects = query.offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for project in projects:
        # Obtener etiquetas
        project_tags = db.query(ProjectTag).join(ProjectTag.tag).filter(ProjectTag.project_id == project.id).all()
        tags_list = [tag.tag.name for tag in project_tags]
        
        # Obtener nombre del propietario
        owner = db.query(User).filter(User.id == project.owner_id).first()
        owner_name = owner.full_name if owner else "Desconocido"
        
        # Obtener categoría y ubicación
        category = project.category.name if project.category else None
        location = project.location.name if project.location else None
        
        # Convertir estado de español a inglés
        status_mapping = {
            "Activo": "active",
            "Inactivo": "inactive", 
            "Completado": "completed"
        }
        status = status_mapping.get(project.status.name, "active") if project.status else "active"
        
        # Contar actividades y documentos
        from ..models.activity import ProjectActivity
        from ..models.document import ProjectDocument
        
        activities_count = db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).count()
        documents_count = db.query(ProjectDocument).filter(ProjectDocument.project_id == project.id).count()
        
        # Verificar si tiene BMC
        from ..models.business_model_canvas import BusinessModelCanvas
        has_bmc = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project.id).first() is not None
        
        project_data = ProjectWithDetails(
            id=project.id,
            name=project.name,
            description=project.description,
            category=category or "Sin categoría",
            location=location or "Sin ubicación",
            status=status,
            owner_id=project.owner_id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            tags=tags_list,
            owner_name=owner_name,
            activities_count=activities_count,
            documents_count=documents_count,
            has_business_model_canvas=has_bmc
        )
        result.append(project_data)
    
    return result

@router.get("/categories")
async def get_project_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de categorías únicas de proyectos"""
    
    categories = db.query(Category.name).join(Project).filter(Project.company_id == current_user.company_id).distinct().all()
    return [category[0] for category in categories if category[0]]

@router.get("/locations")
async def get_project_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de ubicaciones únicas de proyectos"""
    
    locations = db.query(Location.name).join(Project).filter(Project.company_id == current_user.company_id).distinct().all()
    return [location[0] for location in locations if location[0]]

@router.get("/tags")
async def get_project_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de etiquetas únicas de proyectos"""
    
    tags = db.query(Tag.name).join(ProjectTag).distinct().all()
    return [tag[0] for tag in tags if tag[0]]

@router.get("/{project_id}", response_model=ProjectWithDetails)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener proyecto por ID"""
    
    try:
        # Buscando proyecto
        
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.company_id == current_user.company_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proyecto no encontrado"
            )
        
    except Exception as e:
        print(f"Error al obtener proyecto {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
    
    try:
        # Obtener etiquetas
        project_tags = db.query(ProjectTag).join(ProjectTag.tag).filter(ProjectTag.project_id == project.id).all()
        tags_list = [tag.tag.name for tag in project_tags]
        
        # Obtener nombre del propietario
        owner = db.query(User).filter(User.id == project.owner_id).first()
        owner_name = owner.full_name if owner else "Desconocido"
        
        # Contar actividades y documentos
        from ..models.activity import ProjectActivity
        from ..models.document import ProjectDocument
        
        activities_count = db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).count()
        documents_count = db.query(ProjectDocument).filter(ProjectDocument.project_id == project.id).count()
        
        # Verificar si tiene BMC
        from ..models.business_model_canvas import BusinessModelCanvas
        has_bmc = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project.id).first() is not None
        
        # Convertir estado de español a inglés
        status_mapping = {
            "Activo": "active",
            "Inactivo": "inactive", 
            "Completado": "completed"
        }
        status = status_mapping.get(project.status.name, "active") if project.status else "active"
        
        result = ProjectWithDetails(
            id=project.id,
            name=project.name,
            description=project.description,
            category=project.category.name if project.category else None,
            location=project.location.name if project.location else None,
            status=status,
            owner_id=project.owner_id,
            created_at=project.created_at,
            updated_at=project.updated_at,
            tags=tags_list,
            owner_name=owner_name,
            activities_count=activities_count,
            documents_count=documents_count,
            has_business_model_canvas=has_bmc
        )
        return result
    except Exception as e:
        print(f"Error al procesar proyecto {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo proyecto"""
    
    # Obtener o crear categoría
    category = db.query(Category).filter(Category.name == project_data.category).first()
    if not category:
        category = Category(name=project_data.category, company_id=current_user.company_id)
        db.add(category)
        db.commit()

    # Obtener o crear ubicación
    location = db.query(Location).filter(Location.name == project_data.location).first()
    if not location:
        location = Location(name=project_data.location, company_id=current_user.company_id)
        db.add(location)
        db.commit()

    # Convertir estado de inglés a español
    status_mapping = {
        "active": "Activo",
        "inactive": "Inactivo", 
        "completed": "Completado"
    }
    status_name = status_mapping.get(project_data.status, "Activo")
    
    # Obtener o crear estado
    status = db.query(Status).filter(Status.name == status_name).first()
    if not status:
        status = Status(name=status_name, company_id=current_user.company_id)
        db.add(status)
        db.commit()

    # Crear proyecto
    db_project = Project(
        name=project_data.name,
        description=project_data.description,
        category_id=category.id,
        location_id=location.id,
        status_id=status.id,
        owner_id=current_user.id,
        company_id=current_user.company_id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Crear etiquetas si se proporcionan
    if project_data.tags:
        for tag_name in project_data.tags:
            # Obtener o crear etiqueta
            tag = db.query(Tag).filter(Tag.name == tag_name.strip()).first()
            if not tag:
                tag = Tag(name=tag_name.strip(), company_id=current_user.company_id)
                db.add(tag)
                db.commit()
            
            # Crear relación proyecto-etiqueta
            project_tag = ProjectTag(project_id=db_project.id, tag_id=tag.id)
            db.add(project_tag)
        db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_project",
        entity_type="project",
        entity_id=str(db_project.id),
        details=f"Proyecto creado: {db_project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    # Devolver proyecto con detalles
    # Convertir estado de español a inglés para la respuesta
    status_mapping = {
        "Activo": "active",
        "Inactivo": "inactive", 
        "Completado": "completed"
    }
    response_status = status_mapping.get(status.name, "active")
    
    return ProjectWithDetails(
         id=db_project.id,
         name=db_project.name,
         description=db_project.description,
         category=category.name,
         location=location.name,
         status=response_status,
         owner_id=db_project.owner_id,
         created_at=db_project.created_at,
         updated_at=db_project.updated_at,
         tags=[tag.name for tag in db.query(Tag).join(ProjectTag).filter(ProjectTag.project_id == db_project.id).all()],
         owner_name=current_user.full_name,
         activities_count=0,
         documents_count=0,
         has_business_model_canvas=False
     )

@router.put("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar permisos: solo el propietario o admin puede actualizar
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este proyecto"
        )
    
    # Actualizar campos del proyecto
    update_data = project_data.dict(exclude_unset=True)
    tags_to_update = update_data.pop("tags", None)
    
    # Actualizar categoría si se proporciona
    if "category" in update_data:
        category = db.query(Category).filter(Category.name == update_data["category"]).first()
        if not category:
            category = Category(name=update_data["category"], company_id=current_user.company_id)
            db.add(category)
            db.commit()
        project.category_id = category.id
        update_data.pop("category")
    
    # Actualizar ubicación si se proporciona
    if "location" in update_data:
        location = db.query(Location).filter(Location.name == update_data["location"]).first()
        if not location:
            location = Location(name=update_data["location"], company_id=current_user.company_id)
            db.add(location)
            db.commit()
        project.location_id = location.id
        update_data.pop("location")
    
    # Actualizar estado si se proporciona
    if "status" in update_data:
        # Convertir estado de inglés a español
        status_mapping = {
            "active": "Activo",
            "inactive": "Inactivo", 
            "completed": "Completado"
        }
        status_name = status_mapping.get(update_data["status"], "Activo")
        
        status = db.query(Status).filter(Status.name == status_name).first()
        if not status:
            status = Status(name=status_name, company_id=current_user.company_id)
            db.add(status)
            db.commit()
        project.status_id = status.id
        update_data.pop("status")
    
    # Actualizar otros campos
    for field, value in update_data.items():
        setattr(project, field, value)
    
    # Actualizar etiquetas si se proporcionan
    if tags_to_update is not None:
        # Eliminar etiquetas existentes
        db.query(ProjectTag).filter(ProjectTag.project_id == project_id).delete()
        
        # Crear nuevas etiquetas
        for tag_name in tags_to_update:
            # Obtener o crear etiqueta
            tag = db.query(Tag).filter(Tag.name == tag_name.strip()).first()
            if not tag:
                tag = Tag(name=tag_name.strip(), company_id=current_user.company_id)
                db.add(tag)
                db.commit()
            
            # Crear relación proyecto-etiqueta
            project_tag = ProjectTag(project_id=project_id, tag_id=tag.id)
            db.add(project_tag)
    
    db.commit()
    db.refresh(project)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_project",
        entity_type="project",
        entity_id=str(project_id),
        details=f"Proyecto actualizado: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    # Devolver proyecto con detalles
    # Convertir estado de español a inglés para la respuesta
    status_mapping = {
        "Activo": "active",
        "Inactivo": "inactive", 
        "Completado": "completed"
    }
    response_status = status_mapping.get(project.status.name, "active") if project.status else "active"
    
    return ProjectWithDetails(
        id=project.id,
        name=project.name,
        description=project.description,
        category=project.category.name if project.category else "",
        location=project.location.name if project.location else "",
        status=response_status,
        owner_id=project.owner_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        tags=[tag.name for tag in db.query(Tag).join(ProjectTag).filter(ProjectTag.project_id == project.id).all()],
        owner_name=current_user.full_name,
        activities_count=db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).count(),
        documents_count=db.query(ProjectDocument).filter(ProjectDocument.project_id == project.id).count(),
        has_business_model_canvas=db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project.id).first() is not None
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar proyecto"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar permisos: solo el propietario o admin puede eliminar
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este proyecto"
        )
    
    # Eliminar etiquetas asociadas
    db.query(ProjectTag).filter(ProjectTag.project_id == project_id).delete()
    
    # Eliminar proyecto
    db.delete(project)
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_project",
        entity_type="project",
        entity_id=str(project_id),
        details=f"Proyecto eliminado: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return None

@router.get("/stats/summary")
async def get_projects_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas resumidas de proyectos"""
    
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()
    completed_projects = db.query(Project).filter(Project.status == "completed").count()
    inactive_projects = db.query(Project).filter(Project.status == "inactive").count()
    
    # Proyectos del usuario actual
    user_projects = db.query(Project).filter(Project.owner_id == current_user.id).count()
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "inactive_projects": inactive_projects,
        "user_projects": user_projects
    }

@router.get("/my-projects", response_model=List[ProjectWithDetails])
async def get_my_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener proyectos del usuario actual"""
    
    projects = db.query(Project).filter(Project.owner_id == current_user.id).offset(skip).limit(limit).all()
    
    # Enriquecer con información adicional
    result = []
    for project in projects:
        # Obtener etiquetas
        project_tags = db.query(ProjectTag).filter(ProjectTag.project_id == project.id).all()
        tags_list = [tag.tag_name for tag in project_tags]
        
        # Contar actividades y documentos
        from ..models.activity import ProjectActivity
        from ..models.document import ProjectDocument
        
        activities_count = db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).count()
        documents_count = db.query(ProjectDocument).filter(ProjectDocument.project_id == project.id).count()
        
        # Verificar si tiene BMC
        from ..models.business_model_canvas import BusinessModelCanvas
        has_bmc = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.project_id == project.id).first() is not None
        
        project_data = ProjectWithDetails(
            **project.__dict__,
            tags=tags_list,
            owner_name=current_user.full_name,
            activities_count=activities_count,
            documents_count=documents_count,
            has_business_model_canvas=has_bmc
        )
        result.append(project_data)
    
    return result

