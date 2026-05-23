"""
Конфигурация приложения (настройки из .env)
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения"""
    
    # База данных
    DATABASE_URL: str
    
    # Google Places
    GOOGLE_PLACES_API_KEY: str

    # JWT токены
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # HoReCa API
    HORECA_API_URL: str = "http://localhost:8001"
    HORECA_API_KEY: str = "mock-api-key-12345"

    # CORS — разрешённые origins для фронтенда (через запятую в .env)
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    def get_allowed_origins(self) -> list[str]:
        """Возвращает список разрешённых origins из строки .env"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"  # Игнорировать дополнительные переменные из .env


settings = Settings()
