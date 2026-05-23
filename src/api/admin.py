"""
Admin API эндпоинты (управление пользователями и глобальными настройками)
Доступно только для пользователей с ролью ADMIN.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_db, require_admin
from src.core.security import get_password_hash
from src.models import GlobalSettings, Search, User, UserSettings
from src.schemas.admin import (
    GlobalSettingsResponse,
    GlobalSettingsUpdate,
    UserAdminCreate,
    UserAdminResponse,
    UserAdminUpdate,
)
from src.schemas.search import SearchResponse

router = APIRouter()


# ---------------------------------------------------------------------------
# Управление пользователями
# ---------------------------------------------------------------------------


@router.get("/users/", response_model=List[UserAdminResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 100,
):
    """Получить список всех пользователей системы"""
    return db.query(User).offset(skip).limit(limit).all()


@router.post("/users/", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserAdminCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Создать нового пользователя (только для администратора)"""
    # Проверить уникальность email и username
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
    )
    db.add(user)
    db.flush()

    # Создаём настройки по умолчанию
    user_settings = UserSettings(user_id=user.id)
    db.add(user_settings)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: int,
    user_in: UserAdminUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Редактировать пользователя (только для администратора)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_in.email is not None:
        conflict = db.query(User).filter(User.email == user_in.email, User.id != user_id).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        user.email = user_in.email

    if user_in.username is not None:
        conflict = db.query(User).filter(User.username == user_in.username, User.id != user_id).first()
        if conflict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user.username = user_in.username

    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)

    if user_in.role is not None:
        user.role = user_in.role

    if user_in.is_active is not None:
        user.is_active = user_in.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """Удалить пользователя (только для администратора, нельзя удалить себя)"""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Просмотр поисков
# ---------------------------------------------------------------------------


@router.get("/searches/", response_model=List[SearchResponse])
def list_all_searches(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 100,
):
    """Получить все поиски всех пользователей"""
    return db.query(Search).order_by(Search.created_at.desc()).offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# Глобальные настройки
# ---------------------------------------------------------------------------


@router.get("/settings/", response_model=List[GlobalSettingsResponse])
def list_global_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Получить все глобальные настройки системы"""
    return db.query(GlobalSettings).all()


@router.put("/settings/{key}", response_model=GlobalSettingsResponse)
def update_global_setting(
    key: str,
    setting_in: GlobalSettingsUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Обновить значение глобальной настройки по ключу"""
    setting = db.query(GlobalSettings).filter(GlobalSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")

    setting.value = setting_in.value
    if setting_in.description is not None:
        setting.description = setting_in.description

    db.commit()
    db.refresh(setting)
    return setting
