"""
Модели данных SQLAlchemy для проекта LeadGen Scout.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass


class LeadStatus(str, enum.Enum):
    """Статус лида в воронке."""
    NEW = "New"
    QUALIFIED = "Qualified"
    CONTACTED = "Contacted"
    REJECTED = "Rejected"


class UserRole(str, enum.Enum):
    """Роль пользователя в системе."""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"


class SearchStatus(str, enum.Enum):
    """Статус выполнения поиска."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProposalStatus(str, enum.Enum):
    """Статус коммерческого предложения."""
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class User(Base):
    """Модель пользователя системы."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.AGENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    searches = relationship("Search", back_populates="user")
    proposals = relationship("Proposal", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


class UserSettings(Base):
    """Настройки пользователя."""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    ui_language = Column(String, default="en", nullable=False)  # язык интерфейса
    proposal_language = Column(String, default="en", nullable=False)  # язык КП
    default_radius = Column(Integer, default=5000, nullable=False)  # метры
    default_place_types = Column(JSON, default=list, nullable=False)  # список типов
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id} ui_lang={self.ui_language}>"


class GlobalSettings(Base):
    """Глобальные настройки системы (key-value store)."""

    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<GlobalSettings key={self.key!r}>"


class Search(Base):
    """Модель поиска лидов."""

    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Integer, nullable=False)  # метры
    place_types = Column(JSON, nullable=False)  # список типов заведений
    query_string = Column(String, nullable=True)  # опциональный поисковый запрос
    status = Column(Enum(SearchStatus), default=SearchStatus.PENDING, nullable=False)
    total_found = Column(Integer, default=0, nullable=False)
    qualified_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="searches")
    leads = relationship("Lead", back_populates="search")

    def __repr__(self) -> str:
        return (
            f"<Search id={self.id} user_id={self.user_id} "
            f"status={self.status} qualified={self.qualified_count}>"
        )


class Proposal(Base):
    """Модель коммерческого предложения."""

    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    language = Column(String, nullable=False)  # язык КП (en, de, ru)
    content_text = Column(Text, nullable=False)  # текстовое содержимое
    recommendations = Column(JSON, nullable=True)  # рекомендации от HoReCa API
    pdf_url = Column(String, nullable=True)  # путь к сгенерированному PDF
    status = Column(Enum(ProposalStatus), default=ProposalStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    lead = relationship("Lead", back_populates="proposals")
    user = relationship("User", back_populates="proposals")

    def __repr__(self) -> str:
        return (
            f"<Proposal id={self.id} lead_id={self.lead_id} "
            f"status={self.status} language={self.language}>"
        )



class Lead(Base):
    """Модель лида — заведение, найденное через Google Places API."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_id = Column(Integer, ForeignKey("searches.id"), nullable=True)  # связь с поиском
    google_place_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    rating = Column(Float)
    review_count = Column(Integer)
    last_negative_review_text = Column(Text, nullable=True)
    pain_points = Column(JSON, nullable=True)  # список болевых точек для КП
    status = Column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    search = relationship("Search", back_populates="leads")
    proposals = relationship("Proposal", back_populates="lead")

    __table_args__ = (
        UniqueConstraint("google_place_id", name="uq_lead_place_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Lead id={self.id} name={self.name!r} "
            f"rating={self.rating} status={self.status}>"
        )
