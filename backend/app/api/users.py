from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..core.auth import get_current_admin_user, get_current_user, get_password_hash
from ..database import get_db
from ..models.user import User
from ..models.audit_log import AuditLog
from ..schemas.user import UserCreate, UserUpdate, User as UserSchema

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
async def get_users(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    role: Optional[str] = Query(None, description="Filtrar por rol"),
    active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener lista de usuarios (solo administradores)"""
    
    query = db.query(User)
    
    # Aplicar filtros
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_term)) |
            (User.full_name.ilike(search_term)) |
            (User.email.ilike(search_term))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if active is not None:
        query = query.filter(User.active == active)
    
    # Aplicar paginación
    users = query.offset(skip).limit(limit).all()
    
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener usuario por ID"""
    
    # Verificar permisos: solo puede ver su propio perfil o ser admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario (solo administradores)"""
    
    # Verificar si el username ya existe
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Verificar si el email ya existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_user",
        entity_type="user",
        entity_id=str(db_user.id),
        details=f"Usuario creado: {db_user.username} por {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    
    # Verificar permisos: solo puede actualizar su propio perfil o ser admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar restricciones de rol
    if current_user.role != "admin" and user_data.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar el rol de un usuario"
        )
    
    # Actualizar campos
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_user",
        entity_type="user",
        entity_id=str(user_id),
        details=f"Usuario actualizado: {user.username} por {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Eliminar usuario (solo administradores)"""
    
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir eliminar el propio usuario
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )
    
    # En lugar de eliminar, marcar como inactivo
    user.active = False
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_user",
        entity_type="user",
        entity_id=str(user_id),
        details=f"Usuario desactivado: {user.username} por {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return None

@router.patch("/{user_id}/activate", response_model=UserSchema)
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activar usuario (solo administradores)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    user.active = True
    db.commit()
    db.refresh(user)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="activate_user",
        entity_type="user",
        entity_id=str(user_id),
        details=f"Usuario activado: {user.username} por {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.patch("/{user_id}/deactivate", response_model=UserSchema)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Desactivar usuario (solo administradores)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No permitir desactivar el propio usuario
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propio usuario"
        )
    
    user.active = False
    db.commit()
    db.refresh(user)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="deactivate_user",
        entity_type="user",
        entity_id=str(user_id),
        details=f"Usuario desactivado: {user.username} por {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.get("/stats/summary")
async def get_users_summary(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas resumidas de usuarios (solo administradores)"""
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.active == True).count()
    admin_users = db.query(User).filter(User.role == "admin").count()
    regular_users = db.query(User).filter(User.role == "user").count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "admin_users": admin_users,
        "regular_users": regular_users
    }
