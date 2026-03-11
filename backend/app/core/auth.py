import warnings
import logging

# Configurar warnings ANTES de importar passlib
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*passlib.*", category=UserWarning)

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..models.company import Company

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Configuración de hashing de contraseñas
# Suprimir warning específico de bcrypt/passlib compatibility
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Configuración de HTTP Bearer para APIs
security = HTTPBearer()

# ============================================================================
# FUNCIONES DE HASHING Y TOKENS
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña en texto plano contra hash"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
        return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_company_access_token(username: str, company_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token de acceso específico para una empresa"""
    data = {"sub": username, "company_id": company_id}
    return create_access_token(data, expires_delta)

def create_refresh_token(data: dict) -> str:
    """Crear token de refresco JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Error verificando token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============================================================================
# FUNCIONES DE AUTENTICACIÓN PRINCIPALES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual basado en token JWT (método principal)"""
    logger.debug(f"get_current_user called with token: {token[:20] if token else 'None'}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        logger.debug(f"Token payload username: {username}")
        
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError in get_current_user: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_user_with_company(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual con información de empresa"""
    logger.debug(f"get_current_user_with_company called")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        company_id: int = payload.get("company_id")
        
        if username is None or company_id is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError in get_current_user_with_company: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(
        User.username == username,
        User.company_id == company_id
    ).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_user_http_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual usando HTTP Bearer (para APIs específicas)"""
    logger.debug(f"get_current_user_http_bearer called")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        username: str = payload.get("sub")
        company_id: int = payload.get("company_id")
        
        if username is None or company_id is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWTError in get_current_user_http_bearer: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(
        User.username == username,
        User.company_id == company_id,
        User.active == True
    ).first()
    
    if user is None:
        raise credentials_exception
    
    return user

# ============================================================================
# FUNCIONES DE VERIFICACIÓN DE USUARIO
# ============================================================================

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

async def get_current_active_user_with_company(current_user: User = Depends(get_current_user_with_company)) -> User:
    """Obtener usuario activo actual con empresa"""
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

# ============================================================================
# FUNCIONES DE VERIFICACIÓN DE PERMISOS
# ============================================================================

def check_user_permissions(user: User, required_role: str = None) -> bool:
    """Verificar permisos del usuario"""
    if required_role and user.role != required_role:
        return False
    return True

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario administrador actual"""
    if not check_user_permissions(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return current_user

async def get_current_super_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario super administrador actual"""
    if not check_user_permissions(current_user, "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de super administrador"
        )
    return current_user

# ============================================================================
# FUNCIONES DE EMPRESA
# ============================================================================

async def get_current_company(current_user: User = Depends(get_current_user)) -> Company:
    """Obtener la empresa del usuario actual"""
    return current_user.company

def get_company_filter(current_user: User = Depends(get_current_user)) -> dict:
    """Obtener filtro de empresa para consultas"""
    return {"company_id": current_user.company_id}

def verify_company_access(
    resource_company_id: int,
    current_user: User = Depends(get_current_user)
) -> bool:
    """Verificar que el usuario tenga acceso al recurso de la empresa"""
    if current_user.role == "super_admin":
        return True  # Super admin puede acceder a todo
    
    if current_user.company_id != resource_company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este recurso de la empresa"
        )
    
    return True

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_user_company_id(token: str) -> int:
    """Obtener ID de empresa desde token"""
    try:
        payload = verify_token(token)
        company_id = payload.get("company_id")
        if company_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene información de empresa"
            )
        return company_id
    except JWTError as e:
        logger.error(f"Error obteniendo company_id del token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def require_role(required_role: str):
    """Decorador para verificar roles específicos"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role == "super_admin":
            return current_user  # Super admin puede hacer todo
        
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para esta operación"
            )
        return current_user
    
    return role_checker

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Verificar que el usuario sea admin o super_admin"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user

def require_super_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Verificar que el usuario sea super_admin"""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de super administrador"
        )
    return current_user

# ============================================================================
# FUNCIONES DE VALIDACIÓN DE TOKENS
# ============================================================================

def validate_token_format(token: str) -> bool:
    """Validar formato básico del token"""
    if not token or not isinstance(token, str):
        return False
    
    # Verificar que tenga el formato JWT básico (3 partes separadas por puntos)
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    return True

def extract_token_info(token: str) -> Dict[str, Any]:
    """Extraer información del token sin verificar la firma"""
    try:
        # Decodificar sin verificar la firma para obtener información básica
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except JWTError:
        return {}

# ============================================================================
# FUNCIONES DE LOGGING Y AUDITORÍA
# ============================================================================

def log_auth_event(event_type: str, username: str, success: bool, details: str = ""):
    """Registrar eventos de autenticación"""
    logger.info(f"Auth Event: {event_type} - User: {username} - Success: {success} - Details: {details}")

def log_security_event(event_type: str, username: str, ip_address: str = "", details: str = ""):
    """Registrar eventos de seguridad"""
    logger.warning(f"Security Event: {event_type} - User: {username} - IP: {ip_address} - Details: {details}")

# ============================================================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================================================

def get_auth_config() -> Dict[str, Any]:
    """Obtener configuración de autenticación"""
    return {
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
        "algorithm": settings.ALGORITHM,
        "token_url": "api/auth/login"
    }

def update_auth_config(new_config: Dict[str, Any]):
    """Actualizar configuración de autenticación (para futuras implementaciones)"""
    # Esta función se puede implementar para permitir cambios dinámicos
    logger.info(f"Auth config update requested: {new_config}")
    pass