"""
Модуль для работы с базой данных SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import Base

# Загружаем переменные окружения
load_dotenv()

# URL базы данных по умолчанию
DEFAULT_DATABASE_URL = "sqlite:///leadgen.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Создаем engine и SessionLocal на уровне модуля
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine():
    """
    Возвращает SQLAlchemy engine.
    """
    return engine

def init_db():
    """
    Инициализирует базу данных, создавая все таблицы.
    """
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("База данных успешно инициализирована.")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        raise

def get_session() -> Session:
    """
    Создает и возвращает новую сессию базы данных.
    """
    return SessionLocal()
