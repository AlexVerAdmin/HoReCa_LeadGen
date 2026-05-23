"""
Pydantic-схемы для взаимодействия с HoReCa API
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class HoRecaRecommendationRequest(BaseModel):
    """Запрос на получение рекомендаций по лиду"""
    lead: Dict[str, Any]
    language: str = "ru"


class HoRecaRecommendationResponse(BaseModel):
    """Ответ с рекомендациями для лида"""
    recommendations: List[str]
    key_selling_points: List[str]


class HoRecaProposalRequest(BaseModel):
    """Запрос на генерацию коммерческого предложения"""
    lead: Dict[str, Any]
    language: str = "ru"
    include_pricing: bool = True
    template: str = "default"


class HoRecaProposalResponse(BaseModel):
    """Ответ с готовым коммерческим предложением"""
    proposal_id: str
    title: str
    content_html: str
    content_text: str
    pdf_url: Optional[str] = None
    generated_at: datetime
