from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import json

from ..core.auth import get_current_user, get_current_admin_user
from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.business_model_canvas import BusinessModelCanvas
from ..models.audit_log import AuditLog
from ..schemas.business_model_canvas import (
    BusinessModelCanvasCreate, 
    BusinessModelCanvasUpdate, 
    BusinessModelCanvas as BusinessModelCanvasSchema
)

router = APIRouter()

@router.get("/", response_model=List[BusinessModelCanvasSchema])
async def get_business_model_canvases(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    project_id: Optional[int] = Query(None, description="Filtrar por proyecto"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de Business Model Canvas"""
    
    query = db.query(BusinessModelCanvas)
    
    if project_id:
        query = query.filter(BusinessModelCanvas.project_id == project_id)
    
    # Aplicar paginación
    canvases = query.offset(skip).limit(limit).all()
    
    return canvases

@router.get("/project/{project_id}")
async def get_project_business_model_canvas(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Getting BMC for project {project_id} by user {current_user.email}")
    """Obtener Business Model Canvas de un proyecto específico"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Buscar el BMC del proyecto
    canvas = db.query(BusinessModelCanvas).filter(
        BusinessModelCanvas.project_id == project_id
    ).first()
    
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business Model Canvas no encontrado para este proyecto"
        )
    
    # Procesar los datos del BMC para convertir strings a arrays
    def parse_field(field_value):
        if not field_value:
            return []
        try:
            # Intentar parsear como JSON
            return json.loads(field_value)
        except json.JSONDecodeError:
            # Si no es JSON válido, tratar como string separado por comas
            if isinstance(field_value, str):
                return [item.strip() for item in field_value.split(',') if item.strip()]
            return []
    
    # Crear objeto procesado
    processed_canvas = {
        "id": canvas.id,
        "project_id": canvas.project_id,
        "key_partners": parse_field(canvas.key_partners),
        "key_activities": parse_field(canvas.key_activities),
        "key_resources": parse_field(canvas.key_resources),
        "value_propositions": parse_field(canvas.value_propositions),
        "customer_relationships": parse_field(canvas.customer_relationships),
        "channels": parse_field(canvas.channels),
        "customer_segments": parse_field(canvas.customer_segments),
        "cost_structure": parse_field(canvas.cost_structure),
        "revenue_streams": parse_field(canvas.revenue_streams),
        "created_at": canvas.created_at.isoformat() if canvas.created_at else None,
        "updated_at": canvas.updated_at.isoformat() if canvas.updated_at else None
    }
    
    return processed_canvas

@router.get("/test/{project_id}")
async def test_get_project_business_model_canvas(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Endpoint de prueba sin autenticación para obtener BMC"""
    
    # Buscar el BMC del proyecto
    canvas = db.query(BusinessModelCanvas).filter(
        BusinessModelCanvas.project_id == project_id
    ).first()
    
    if not canvas:
        return {"error": "BMC no encontrado"}
    
    # Procesar los datos del BMC para convertir strings a arrays
    def parse_field(field_value):
        if not field_value:
            return []
        try:
            # Intentar parsear como JSON
            return json.loads(field_value)
        except json.JSONDecodeError:
            # Si no es JSON válido, tratar como string separado por comas
            if isinstance(field_value, str):
                return [item.strip() for item in field_value.split(',') if item.strip()]
            return []
    
    # Crear objeto procesado
    processed_canvas = {
        "id": canvas.id,
        "project_id": canvas.project_id,
        "key_partners": parse_field(canvas.key_partners),
        "key_activities": parse_field(canvas.key_activities),
        "key_resources": parse_field(canvas.key_resources),
        "value_propositions": parse_field(canvas.value_propositions),
        "customer_relationships": parse_field(canvas.customer_relationships),
        "channels": parse_field(canvas.channels),
        "customer_segments": parse_field(canvas.customer_segments),
        "cost_structure": parse_field(canvas.cost_structure),
        "revenue_streams": parse_field(canvas.revenue_streams),
        "created_at": canvas.created_at,
        "updated_at": canvas.updated_at
    }
    
    return processed_canvas

@router.post("/", response_model=BusinessModelCanvasSchema, status_code=status.HTTP_201_CREATED)
async def create_business_model_canvas(
    canvas_data: BusinessModelCanvasCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo Business Model Canvas"""
    
    # Verificar que el proyecto existe
    project = db.query(Project).filter(Project.id == canvas_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede crear BMC
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear Business Model Canvas en este proyecto"
        )
    
    # Verificar que no exista ya un BMC para este proyecto
    existing_canvas = db.query(BusinessModelCanvas).filter(
        BusinessModelCanvas.project_id == canvas_data.project_id
    ).first()
    
    if existing_canvas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un Business Model Canvas para este proyecto"
        )
    
    # Crear BMC
    db_canvas = BusinessModelCanvas(
        project_id=canvas_data.project_id,
        key_partners=json.dumps(canvas_data.key_partners) if canvas_data.key_partners else None,
        key_activities=json.dumps(canvas_data.key_activities) if canvas_data.key_activities else None,
        key_resources=json.dumps(canvas_data.key_resources) if canvas_data.key_resources else None,
        value_propositions=json.dumps(canvas_data.value_propositions) if canvas_data.value_propositions else None,
        customer_relationships=json.dumps(canvas_data.customer_relationships) if canvas_data.customer_relationships else None,
        channels=json.dumps(canvas_data.channels) if canvas_data.channels else None,
        customer_segments=json.dumps(canvas_data.customer_segments) if canvas_data.customer_segments else None,
        cost_structure=json.dumps(canvas_data.cost_structure) if canvas_data.cost_structure else None,
        revenue_streams=json.dumps(canvas_data.revenue_streams) if canvas_data.revenue_streams else None
    )
    
    db.add(db_canvas)
    db.commit()
    db.refresh(db_canvas)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_business_model_canvas",
        entity_type="business_model_canvas",
        entity_id=str(db_canvas.id),
        details=f"Business Model Canvas creado para proyecto: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_canvas

@router.put("/{canvas_id}", response_model=BusinessModelCanvasSchema)
async def update_business_model_canvas(
    canvas_id: int,
    canvas_data: BusinessModelCanvasUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar Business Model Canvas"""
    
    # Verificar que el BMC existe
    canvas = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.id == canvas_id).first()
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business Model Canvas no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede actualizar
    project = db.query(Project).filter(Project.id == canvas.project_id).first()
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este Business Model Canvas"
        )
    
    # Actualizar campos
    update_data = canvas_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            # Convertir listas a JSON strings
            if isinstance(value, list):
                setattr(canvas, field, json.dumps(value))
            else:
                setattr(canvas, field, value)
    
    db.commit()
    db.refresh(canvas)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_business_model_canvas",
        entity_type="business_model_canvas",
        entity_id=str(canvas_id),
        details=f"Business Model Canvas actualizado para proyecto: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return canvas

@router.patch("/{canvas_id}/element")
async def update_canvas_element(
    canvas_id: int,
    element_name: str,
    element_data: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar un elemento específico del Business Model Canvas"""
    
    # Verificar que el BMC existe
    canvas = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.id == canvas_id).first()
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business Model Canvas no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede actualizar
    project = db.query(Project).filter(Project.id == canvas.project_id).first()
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este Business Model Canvas"
        )
    
    # Validar nombre del elemento
    valid_elements = [
        "key_partners", "key_activities", "key_resources", "value_propositions",
        "customer_relationships", "channels", "customer_segments", "cost_structure", "revenue_streams"
    ]
    
    if element_name not in valid_elements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Elemento inválido. Elementos válidos: {', '.join(valid_elements)}"
        )
    
    # Actualizar elemento específico
    setattr(canvas, element_name, json.dumps(element_data))
    db.commit()
    db.refresh(canvas)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_canvas_element",
        entity_type="business_model_canvas",
        entity_id=str(canvas_id),
        details=f"Elemento '{element_name}' actualizado en BMC del proyecto: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "message": f"Elemento '{element_name}' actualizado exitosamente",
        "element_data": element_data
    }

@router.delete("/{canvas_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business_model_canvas(
    canvas_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar Business Model Canvas"""
    
    # Verificar que el BMC existe
    canvas = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.id == canvas_id).first()
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business Model Canvas no encontrado"
        )
    
    # Verificar permisos: solo el propietario del proyecto o admin puede eliminar
    project = db.query(Project).filter(Project.id == canvas.project_id).first()
    if project.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este Business Model Canvas"
        )
    
    # Eliminar BMC
    db.delete(canvas)
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_business_model_canvas",
        entity_type="business_model_canvas",
        entity_id=str(canvas_id),
        details=f"Business Model Canvas eliminado del proyecto: {project.name}"
    )
    db.add(audit_log)
    db.commit()
    
    return None

@router.get("/{canvas_id}/export")
async def export_business_model_canvas(
    canvas_id: int,
    format: str = Query("json", description="Formato de exportación (json, csv)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exportar Business Model Canvas en diferentes formatos"""
    
    # Verificar que el BMC existe
    canvas = db.query(BusinessModelCanvas).filter(BusinessModelCanvas.id == canvas_id).first()
    if not canvas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business Model Canvas no encontrado"
        )
    
    # Obtener información del proyecto
    project = db.query(Project).filter(Project.id == canvas.project_id).first()
    
    # Preparar datos para exportación
    export_data = {
        "project_name": project.name if project else "Desconocido",
        "project_id": canvas.project_id,
        "created_at": canvas.created_at.isoformat() if canvas.created_at else None,
        "updated_at": canvas.updated_at.isoformat() if canvas.updated_at else None,
        "elements": {}
    }
    
    # Agregar elementos del canvas
    elements = [
        "key_partners", "key_activities", "key_resources", "value_propositions",
        "customer_relationships", "channels", "customer_segments", "cost_structure", "revenue_streams"
    ]
    
    for element in elements:
        element_value = getattr(canvas, element)
        if element_value:
            try:
                export_data["elements"][element] = json.loads(element_value)
            except json.JSONDecodeError:
                export_data["elements"][element] = element_value
        else:
            export_data["elements"][element] = []
    
    if format.lower() == "json":
        return export_data
    elif format.lower() == "csv":
        # Implementar exportación CSV si es necesario
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato CSV no implementado aún"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado. Use 'json' o 'csv'"
        )

@router.get("/stats/summary")
async def get_bmc_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas resumidas de Business Model Canvas"""
    
    total_canvases = db.query(BusinessModelCanvas).count()
    
    # Contar proyectos con BMC
    projects_with_bmc = db.query(Project).join(BusinessModelCanvas).count()
    total_projects = db.query(Project).count()
    
    # Contar elementos completados por BMC
    completed_elements = 0
    total_elements = 0
    
    canvases = db.query(BusinessModelCanvas).all()
    for canvas in canvases:
        elements = [
            canvas.key_partners, canvas.key_activities, canvas.key_resources,
            canvas.value_propositions, canvas.customer_relationships, canvas.channels,
            canvas.customer_segments, canvas.cost_structure, canvas.revenue_streams
        ]
        
        for element in elements:
            total_elements += 1
            if element and element.strip():
                completed_elements += 1
    
    completion_rate = (completed_elements / total_elements * 100) if total_elements > 0 else 0
    
    return {
        "total_canvases": total_canvases,
        "projects_with_bmc": projects_with_bmc,
        "total_projects": total_projects,
        "completion_rate_percent": round(completion_rate, 2),
        "completed_elements": completed_elements,
        "total_elements": total_elements
    }

