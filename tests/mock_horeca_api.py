"""
Mock-сервер HoReCa API для локального тестирования.
Запуск: uvicorn tests.mock_horeca_api:app --port 8001 --reload
"""
from datetime import datetime, timezone
from typing import Any, Dict
import uuid

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Mock HoReCa API", version="1.0.0")

# Тестовый API-ключ
VALID_API_KEY = "mock-api-key-12345"


# --- Pydantic-модели запросов ---

class RecommendationRequest(BaseModel):
    lead: Dict[str, Any]
    language: str = "ru"


class ProposalRequest(BaseModel):
    lead: Dict[str, Any]
    language: str = "ru"
    include_pricing: bool = True
    template: str = "default"


# --- Хелпер авторизации ---

def _check_api_key(x_api_key: str):
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


# --- Эндпоинты ---

@app.post("/recommendations")
async def get_recommendations(
    body: RecommendationRequest,
    x_api_key: str = Header(...),
):
    """Вернуть mock-рекомендации для лида"""
    _check_api_key(x_api_key)

    lead_name = body.lead.get("name", "Заведение")
    pain_points = body.lead.get("pain_points", [])

    # Генерируем рекомендации на основе pain_points
    recommendations = []
    if "низкий рейтинг" in str(pain_points).lower() or body.lead.get("rating", 5) < 4:
        recommendations.append(
            f"Для {lead_name} рекомендуем программу улучшения клиентского сервиса"
        )
    if "мало отзывов" in str(pain_points).lower() or body.lead.get("review_count", 100) < 50:
        recommendations.append(
            f"{lead_name} выиграет от активной работы с отзывами"
        )
    if not recommendations:
        recommendations.append(
            f"{lead_name} подходит для нашего комплексного предложения"
        )

    return {
        "recommendations": recommendations,
        "key_selling_points": [
            "Увеличение среднего чека на 15%",
            "Снижение стоимости привлечения клиента",
            "Автоматизация работы с отзывами",
        ],
    }


@app.post("/proposals")
async def generate_proposal(
    body: ProposalRequest,
    x_api_key: str = Header(...),
):
    """Сгенерировать mock коммерческое предложение"""
    _check_api_key(x_api_key)

    lead_name = body.lead.get("name", "Заведение")
    proposal_id = str(uuid.uuid4())
    title = f"Коммерческое предложение для {lead_name}"

    content_text = (
        f"{title}\n\n"
        f"Уважаемые представители {lead_name},\n\n"
        f"Предлагаем вам наше решение для развития бизнеса.\n\n"
    )
    if body.include_pricing:
        content_text += "Стоимость: от 990 EUR/мес.\n\n"

    content_html = f"<h1>{title}</h1><p>{content_text.replace(chr(10), '<br>')}</p>"

    return {
        "proposal_id": proposal_id,
        "title": title,
        "content_html": content_html,
        "content_text": content_text,
        "pdf_url": None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mock-horeca-api"}
