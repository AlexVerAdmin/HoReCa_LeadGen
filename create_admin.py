"""
Скрипт для создания первого администратора
"""
from src.database import get_session, init_db
from src.models import User, UserSettings, UserRole
from src.core.security import get_password_hash


def create_admin():
    """Создание первого администратора"""
    init_db()  # Убедимся что БД инициализирована
    
    session = get_session()
    
    # Проверка что админ еще не создан
    existing_admin = session.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        print(f"Администратор уже существует: {existing_admin.email}")
        return
    
    # Создание администратора
    admin_email = "admin@example.com"
    admin_password = "admin123"  # В production использовать безопасный пароль
    
    admin = User(
        email=admin_email,
        username="admin",
        hashed_password=get_password_hash(admin_password),
        role=UserRole.ADMIN,
        is_active=True
    )
    
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    # Создание настроек для администратора
    admin_settings = UserSettings(
        user_id=admin.id,
        ui_language="ru",
        proposal_language="ru",
        default_radius=5000,
        default_place_types=["restaurant", "cafe", "bar"]
    )
    
    session.add(admin_settings)
    session.commit()
    
    print(f"✓ Администратор создан:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print(f"  ID: {admin.id}")


if __name__ == "__main__":
    create_admin()
