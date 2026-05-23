"""
Интеграционный тест взаимодействия Vue.js фронтенда с API.
Симулирует реальный flow: логин -> передача JWT -> запрос защищённых ресурсов.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # гарантирует одно соединение для in-memory SQLite

from app import app
from src.models import Base, User, UserRole, UserSettings  # импорт Base из models — все таблицы зарегистрированы
from src.api.deps import get_db
from src.core.security import get_password_hash


# --- Настройка тестовой БД в памяти ---

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

# StaticPool: все сессии делят ОДНО соединение, иначе in-memory SQLite
# создаёт отдельную пустую БД на каждое новое соединение
engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Подменяем зависимость БД на тестовую"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Создаём таблицы перед каждым тестом, очищаем после"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_user():
    """Создаём тестового администратора напрямую в БД вместе с его UserSettings"""
    db = TestingSessionLocal()
    user = User(
        email="admin@test.com",
        username="admin",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    # создаём настройки, т.к. обходим /register
    settings_obj = UserSettings(
        user_id=user.id,
        ui_language="ru",
        proposal_language="ru",
        default_radius=5000,
        default_place_types=["restaurant"],
    )
    db.add(settings_obj)
    db.commit()
    db.close()
    return user


def get_auth_headers(client: TestClient, email: str, password: str) -> dict:
    """Получаем JWT и возвращаем заголовок Authorization — как это делает Vue.js axios"""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Тесты ---

class TestFrontendAuthFlow:
    """Тестирует авторизационный flow как Vue.js фронтенд"""

    def test_preflight_options_cors(self, client):
        """Браузер отправляет OPTIONS preflight перед реальным запросом"""
        response = client.options(
            "/api/auth/login",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization",
            },
        )
        # 200 или 204 — preflight прошёл
        assert response.status_code in (200, 204)

    def test_login_returns_tokens(self, client, admin_user):
        """После логина фронтенд получает access_token и refresh_token"""
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_protected_endpoint_without_token_returns_401(self, client, admin_user):
        """Запрос без токена должен вернуть 401 — фронтенд редиректит на login"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_bearer_token(self, client, admin_user):
        """Фронтенд передаёт токен в заголовке Authorization: Bearer <token>"""
        headers = get_auth_headers(client, "admin@test.com", "testpass123")
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"

    def test_invalid_token_returns_401(self, client, admin_user):
        """Невалидный или устаревший токен -> 401 -> фронтенд вызывает refresh"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401

    def test_refresh_token_flow(self, client, admin_user):
        """Фронтенд обновляет access_token через refresh_token"""
        login = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "testpass123"},
        )
        refresh_token = login.json()["refresh_token"]

        # refresh_token передаётся как query-параметр (не JSON body)
        response = client.post(
            f"/api/auth/refresh?refresh_token={refresh_token}",
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestFrontendUserSettings:
    """Тестирует flow управления настройками пользователя"""

    def test_get_user_settings(self, client, admin_user):
        """Фронтенд загружает настройки при инициализации"""
        headers = get_auth_headers(client, "admin@test.com", "testpass123")
        response = client.get("/api/users/me/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Проверяем, что ответ содержит ожидаемые поля настроек
        assert "ui_language" in data
        assert "proposal_language" in data

    def test_update_user_settings(self, client, admin_user):
        """Фронтенд сохраняет настройки пользователя"""
        headers = get_auth_headers(client, "admin@test.com", "testpass123")
        response = client.put(
            "/api/users/me/settings",
            json={"ui_language": "de", "proposal_language": "de"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ui_language"] == "de"
        assert data["proposal_language"] == "de"


class TestFrontendAdminFlow:
    """Тестирует admin-панель"""

    def test_admin_can_list_users(self, client, admin_user):
        """Страница admin/users загружает список пользователей"""
        headers = get_auth_headers(client, "admin@test.com", "testpass123")
        response = client.get("/api/admin/users/", headers=headers)
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 1

    def test_admin_can_create_user(self, client, admin_user):
        """Форма создания пользователя в admin-панели"""
        headers = get_auth_headers(client, "admin@test.com", "testpass123")
        response = client.post(
            "/api/admin/users/",
            json={
                "email": "manager@test.com",
                "username": "manager",
                "password": "managerpass123",
                "role": "manager",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "manager@test.com"
        assert data["role"] == "manager"
