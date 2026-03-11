from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_company_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    get_current_user_with_company,
    get_user_company_id
)
from ..database import get_db
from ..models.user import User
from ..models.company import Company
from ..models.audit_log import AuditLog
from ..schemas.user import UserCreate, User as UserSchema, UserLogin
from ..schemas.token import Token, RefreshToken
from ..config import settings

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    
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
    
    # Verificar que la empresa existe
    company = db.query(Company).filter(Company.id == user_data.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa especificada no existe"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        company_id=user_data.company_id,
        active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=db_user.id,
        action="register",
        entity_type="user",
        entity_id=str(db_user.id),
        details=f"Usuario registrado: {db_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_user

@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Iniciar sesión de usuario"""
    
    # Buscar usuario por username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crear tokens con company_id
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_company_access_token(
        username=user.username,
        company_id=user.company_id,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "company_id": user.company_id}
    )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=str(user.id),
        details=f"Usuario inició sesión: {user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # en segundos
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Renovar token de acceso usando refresh token"""
    
    try:
        # Verificar refresh token
        payload = verify_token(refresh_data.refresh_token)
        
        # Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido para refresco"
            )
        
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no válido o inactivo"
            )
        
        # Crear nuevo access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_company_access_token(
            username=user.username,
            company_id=user.company_id,
            expires_delta=access_token_expires
        )
        
        # Crear nuevo refresh token
        new_refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id, "company_id": user.company_id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": new_refresh_token
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido"
        )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cerrar sesión de usuario"""
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="logout",
        entity_type="user",
        entity_id=str(current_user.id),
        details=f"Usuario cerró sesión: {current_user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Sesión cerrada exitosamente"}

@router.post("/login-company", response_model=Token)
async def login_user_with_company(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Iniciar sesión de usuario con validación de empresa"""
    
    # Buscar usuario por username
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (ValueError, Exception):
        # bcrypt/passlib puede lanzar ValueError (ej. password > 72 bytes); no exponer 500
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Si se especifica company_id, validar que coincida
    if user_data.company_id and user.company_id != user_data.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no pertenece a la empresa especificada"
        )
    
    # Crear tokens con company_id
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_company_access_token(
        username=user.username,
        company_id=user.company_id,
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "company_id": user.company_id}
    )
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=str(user.id),
        details=f"Usuario inició sesión: {user.username}"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # en segundos
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "company_id": user.company_id
        }
    }

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del usuario actual"""
    
    # Verificar contraseña actual
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Actualizar contraseña
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    # Registrar en auditoría
    audit_log = AuditLog(
        user_id=current_user.id,
        action="change_password",
        entity_type="user",
        entity_id=str(current_user.id),
        details="Usuario cambió su contraseña"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Contraseña cambiada exitosamente"}

