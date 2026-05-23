"""
Pydantic-схемы для коммерческих предложений (Proposals)
"""
from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, model_validator

from src.models import ProposalStatus


class ProposalCreate(BaseModel):
    """Запрос на создание коммерческого предложения"""
    lead_id: int
    language: str = "ru"


class ProposalResponse(BaseModel):
    """Ответ с данными коммерческого предложения"""
    id: int
    lead_id: int
    language: str
    content_text: str
    recommendations: Optional[List[Any]] = None
    pdf_url: Optional[str] = None
    status: ProposalStatus
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def map_created_at(cls, data: Any) -> Any:
        """Маппинг created_at -> generated_at для совместимости с моделью БД"""
        if hasattr(data, "__dict__"):
            # ORM-объект: подставляем created_at в generated_at
            obj = {k: v for k, v in data.__dict__.items() if not k.startswith("_")}
            obj.setdefault("generated_at", obj.get("created_at"))
            return obj
        if isinstance(data, dict):
            data.setdefault("generated_at", data.get("created_at"))
        return data


class ProposalStatusUpdate(BaseModel):
    """Обновление статуса коммерческого предложения"""
    status: ProposalStatus
