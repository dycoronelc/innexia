from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.auth import get_current_user, require_admin, require_super_admin
from ..database import get_db
from ..models import Company, User
from ..schemas.company import CompanyResponse, CompanyUpdate

router = APIRouter()

@router.get("/me", response_model=CompanyResponse)
async def get_my_company(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener información de la empresa del usuario actual"""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    return company

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener información de una empresa específica (solo super_admin)"""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los super administradores pueden acceder a esta información"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    return company

@router.get("/", response_model=List[CompanyResponse])
async def get_all_companies(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Obtener todas las empresas (solo super_admin)"""
    companies = db.query(Company).all()
    return companies

@router.put("/me", response_model=CompanyResponse)
async def update_my_company(
    company_data: CompanyUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Actualizar información de la empresa del usuario actual"""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Actualizar campos permitidos
    for field, value in company_data.dict(exclude_unset=True).items():
        setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Crear nueva empresa (solo super_admin)"""
    # Verificar si el slug ya existe
    existing_company = db.query(Company).filter(Company.slug == company_data.slug).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El slug de empresa ya está en uso"
        )
    
    # Crear nueva empresa
    db_company = Company(**company_data.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Eliminar empresa (solo super_admin)"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    # Verificar que no haya usuarios en la empresa
    users_count = db.query(User).filter(User.company_id == company_id).count()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar una empresa que tenga usuarios"
        )
    
    db.delete(company)
    db.commit()
    
    return None
