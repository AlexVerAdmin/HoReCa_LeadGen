"""
Клиент для взаимодействия с HoReCa API
"""
from typing import Any, Dict
import httpx

from src.schemas.horeca import (
    HoRecaRecommendationResponse,
    HoRecaProposalResponse,
)


class HoRecaClient:
    """HTTP-клиент для HoReCa API"""

    def __init__(self, api_url: str, api_key: str):
        # Базовый URL и ключ API
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def get_recommendations(
        self, lead_data: Dict[str, Any], language: str = "ru"
    ) -> dict:
        """Получить рекомендации по лиду от HoReCa API"""
        payload = {"lead": lead_data, "language": language}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_url}/recommendations",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def generate_proposal(
        self,
        lead_data: Dict[str, Any],
        language: str = "ru",
        include_pricing: bool = True,
        template: str = "default",
    ) -> dict:
        """Сгенерировать коммерческое предложение для лида"""
        payload = {
            "lead": lead_data,
            "language": language,
            "include_pricing": include_pricing,
            "template": template,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_url}/proposals",
                json=payload,
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()
