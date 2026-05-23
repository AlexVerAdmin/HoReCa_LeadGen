"""
Users API эндпоинты (профиль и настройки текущего пользователя)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_user
from src.models import User, UserSettings
from src.schemas.user import UserResponse
from src.schemas.settings import UserSettingsResponse, UserSettingsUpdate


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Получить профиль текущего пользователя"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить username текущего пользователя"""
    # Проверить, что username не занят другим пользователем
    existing = db.query(User).filter(
        User.username == username,
        User.id != current_user.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    current_user.username = username
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить настройки текущего пользователя"""
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()

    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )

    return user_settings


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    settings_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить настройки текущего пользователя"""
    user_settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()

    if not user_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found"
        )

    # Обновляем только переданные поля
    update_data = settings_data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user_settings, field, value)

    db.commit()
    db.refresh(user_settings)
    return user_settings
