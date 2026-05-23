"""
Pydantic схемы для User API
"""
from pydantic import BaseModel, EmailStr
from src.models import UserRole


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.AGENT


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема JWT токенов"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
