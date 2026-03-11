from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# UserBase eliminado ya que no es necesario

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default="user", pattern="^(admin|user|super_admin)$")
    company_id: int = Field(..., ge=1, description="ID de la empresa a la que pertenece el usuario")
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|user|super_admin)$")
    company_id: Optional[int] = Field(None, ge=1, description="ID de la empresa a la que pertenece el usuario")
    active: Optional[bool] = None

# UserInDB eliminado ya que no es necesario

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    company_id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str
    company_id: Optional[int] = Field(None, description="ID de la empresa (opcional para login)")

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

