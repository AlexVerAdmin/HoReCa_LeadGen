"""
FastAPI приложение для LeadGen Scout Web UI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import admin, auth, users, searches, leads, proposals


# Создание FastAPI приложения
app = FastAPI(
    title="LeadGen Scout API",
    description="API для поиска и квалификации HoReCa лидов",
    version="1.0.0"
)


# CORS middleware для доступа из браузера
# allow_origins=["*"] несовместим с allow_credentials=True по спецификации CORS,
# поэтому используем явный список origins из настроек
from src.core.config import Settings as _Settings
_settings = _Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(searches.router, prefix="/api/searches", tags=["searches"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["proposals"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "LeadGen Scout API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {"status": "ok"}
