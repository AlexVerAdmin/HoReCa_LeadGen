"""
Pydantic схемы для Admin API (управление пользователями и глобальными настройками)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.models import UserRole


class UserAdminCreate(BaseModel):
    """Схема для создания пользователя администратором"""
    email: EmailStr
    username: str
    password: str
    role: UserRole = UserRole.AGENT
    is_active: bool = True


class UserAdminUpdate(BaseModel):
    """Схема для редактирования пользователя администратором (все поля опциональны)"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserAdminResponse(BaseModel):
    """Расширенная схема пользователя для администратора"""
    id: int
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlobalSettingsResponse(BaseModel):
    """Схема ответа для глобальной настройки (key-value)"""
    id: int
    key: str
    value: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GlobalSettingsUpdate(BaseModel):
    """Схема обновления значения глобальной настройки"""
    value: str
    description: Optional[str] = None
