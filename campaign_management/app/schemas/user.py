from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr  
    full_name: str


class UserCreate(UserBase):
    email: EmailStr 
    password: str
    full_name: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 
    refresh_token: str

class RefreshTokenIn(BaseModel):
    refresh_token: str