"""
Pydantic схемы для UserSettings API
"""
from typing import List, Optional
from pydantic import BaseModel


class UserSettingsResponse(BaseModel):
    """Схема ответа с настройками пользователя"""
    ui_language: str
    proposal_language: str
    default_radius: int
    default_place_types: List[str]

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Схема обновления настроек пользователя (все поля опциональны)"""
    ui_language: Optional[str] = None
    proposal_language: Optional[str] = None
    default_radius: Optional[int] = None
    default_place_types: Optional[List[str]] = None
