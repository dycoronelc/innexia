from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..models.category import Category
from ..models.tag import Tag
from ..models.location import Location
from ..models.status import Status
from ..schemas.category import Category as CategorySchema
from ..schemas.tag import Tag as TagSchema
from ..schemas.location import Location as LocationSchema
from ..schemas.status import Status as StatusSchema

router = APIRouter()

# ============================================================================
# ENDPOINTS CORS PREFLIGHT
# ============================================================================

@router.options("/categories")
async def options_categories():
    """Endpoint OPTIONS para manejar preflight de CORS"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.options("/tags")
async def options_tags():
    """Endpoint OPTIONS para manejar preflight de CORS"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.options("/locations")
async def options_locations():
    """Endpoint OPTIONS para manejar preflight de CORS"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.options("/statuses")
async def options_statuses():
    """Endpoint OPTIONS para manejar preflight de CORS"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# ============================================================================
# CATEGORÍAS
# ============================================================================

@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las categorías de la empresa del usuario"""
    
    # Filtrar por empresa del usuario
    categories = db.query(Category).filter(
        Category.company_id == current_user.company_id,
        Category.active == True
    ).all()
    
    return categories

@router.post("/categories", response_model=CategorySchema)
async def create_category(
    category_data: CategorySchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva categoría"""
    
    # Verificar que el usuario sea admin
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear categorías"
        )
    
    # Crear categoría con company_id del usuario
    new_category = Category(
        name=category_data.name,
        description=category_data.description,
        color=category_data.color,
        active=category_data.active,
        company_id=current_user.company_id
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_data: CategorySchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar categoría"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar categorías"
        )
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.company_id == current_user.company_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    # Actualizar campos
    category.name = category_data.name
    category.description = category_data.description
    category.color = category_data.color
    category.active = category_data.active
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar categoría"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar categorías"
        )
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.company_id == current_user.company_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    db.delete(category)
    db.commit()
    
    return None

# ============================================================================
# ETIQUETAS
# ============================================================================

@router.get("/tags", response_model=List[TagSchema])
async def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las etiquetas de la empresa del usuario"""
    
    tags = db.query(Tag).filter(
        Tag.company_id == current_user.company_id,
        Tag.active == True
    ).all()
    
    return tags

@router.post("/tags", response_model=TagSchema)
async def create_tag(
    tag_data: TagSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva etiqueta"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear etiquetas"
        )
    
    new_tag = Tag(
        **tag_data.model_dump(),
        company_id=current_user.company_id
    )
    
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    
    return new_tag

@router.put("/tags/{tag_id}", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag_data: TagSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar etiqueta"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar etiquetas"
        )
    
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.company_id == current_user.company_id
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada"
        )
    
    # Actualizar campos
    for field, value in tag_data.model_dump().items():
        setattr(tag, field, value)
    
    db.commit()
    db.refresh(tag)
    
    return tag

@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar etiqueta"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar etiquetas"
        )
    
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.company_id == current_user.company_id
    ).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada"
        )
    
    db.delete(tag)
    db.commit()
    
    return None

# ============================================================================
# UBICACIONES
# ============================================================================

@router.get("/locations", response_model=List[LocationSchema])
async def get_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las ubicaciones de la empresa del usuario"""
    
    locations = db.query(Location).filter(
        Location.company_id == current_user.company_id,
        Location.active == True
    ).all()
    
    return locations

@router.post("/locations", response_model=LocationSchema)
async def create_location(
    location_data: LocationSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva ubicación"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear ubicaciones"
        )
    
    new_location = Location(
        **location_data.model_dump(),
        company_id=current_user.company_id
    )
    
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return new_location

@router.put("/locations/{location_id}", response_model=LocationSchema)
async def update_location(
    location_id: int,
    location_data: LocationSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar ubicación"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar ubicaciones"
        )
    
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.company_id == current_user.company_id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ubicación no encontrada"
        )
    
    # Actualizar campos
    for field, value in location_data.model_dump().items():
        setattr(location, field, value)
    
    db.commit()
    db.refresh(location)
    
    return location

@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar ubicación"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar ubicaciones"
        )
    
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.company_id == current_user.company_id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ubicación no encontrada"
        )
    
    db.delete(location)
    db.commit()
    
    return None

# ============================================================================
# ESTADOS
# ============================================================================

@router.get("/statuses", response_model=List[StatusSchema])
async def get_statuses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los estados de la empresa del usuario"""
    
    statuses = db.query(Status).filter(
        Status.company_id == current_user.company_id,
        Status.active == True
    ).all()
    
    return statuses

@router.post("/statuses", response_model=StatusSchema)
async def create_status(
    status_data: StatusSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo estado"""
    
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear estados"
        )
    
    new_status = Status(
        **status_data.model_dump(),
        company_id=current_user.company_id
    )
    
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    
    return new_status
