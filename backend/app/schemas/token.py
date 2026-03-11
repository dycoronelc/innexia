from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    company_id: Optional[int] = None

class RefreshToken(BaseModel):
    refresh_token: str
    username: Optional[str] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None

