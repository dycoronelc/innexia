from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.audit_log import AuditLog
from ..schemas.audit_log import AuditLog as AuditLogSchema

router = APIRouter()

@router.get("/", response_model=List[AuditLogSchema])
async def get_audit_logs(
    action: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener registros de bitácora con filtros opcionales.
    Solo usuarios admin y super_admin pueden ver todas las bitácoras.
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver las bitácoras"
        )
    
    # Construir la consulta base
    query = db.query(AuditLog).join(AuditLog.user)
    
    # Aplicar filtros
    filters = []
    
    if action:
        filters.append(AuditLog.action == action)
    
    if entity_type:
        filters.append(AuditLog.entity_type == entity_type)
    
    if username:
        filters.append(User.username.ilike(f"%{username}%"))
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            filters.append(AuditLog.timestamp >= date_from_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido para date_from. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            # Ajustar al final del día
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            filters.append(AuditLog.timestamp <= date_to_obj)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido para date_to. Use YYYY-MM-DD"
            )
    
    # Aplicar todos los filtros
    if filters:
        query = query.filter(and_(*filters))
    
    # Ordenar por timestamp descendente (más reciente primero)
    query = query.order_by(AuditLog.timestamp.desc())
    
    return query.all()

@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogSchema])
async def get_entity_audit_logs(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener registros de bitácora para una entidad específica.
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver las bitácoras"
        )
    
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.timestamp.desc()).all()
    
    return logs

@router.get("/user/{user_id}", response_model=List[AuditLogSchema])
async def get_user_audit_logs(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener registros de bitácora para un usuario específico.
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver las bitácoras"
        )
    
    logs = db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(AuditLog.timestamp.desc()).all()
    
    return logs
