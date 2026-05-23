"""
API эндпоинты для управления коммерческими предложениями (Proposals).
"""
import os
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from src.api import deps
from src.core.config import settings
from src.models import Lead, Proposal, ProposalStatus, User
from src.schemas.proposal import ProposalCreate, ProposalResponse, ProposalStatusUpdate
from src.services.horeca_client import HoRecaClient
from src.services.pdf_generator import PDFGenerator

router = APIRouter()

# Директория для хранения PDF-файлов
PDF_OUTPUT_DIR = "media/proposals"

# Директория с Jinja2-шаблонами
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"


def _get_horeca_client() -> HoRecaClient:
    """Создаёт экземпляр HoReCa API клиента из настроек"""
    return HoRecaClient(
        api_url=settings.HORECA_API_URL,
        api_key=settings.HORECA_API_KEY,
    )


def _render_proposal_html(
    lead: Lead,
    content_text: str,
    recommendations: list,
    language: str,
    generated_at: datetime,
) -> str:
    """Рендерит HTML-шаблон КП через Jinja2"""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("proposal_template.html")
    return template.render(
        title=f"Коммерческое предложение — {lead.name}",
        lead_name=lead.name,
        lead_address=lead.address or "",
        lead_rating=lead.rating,
        lead_review_count=lead.review_count,
        pain_points=lead.pain_points or [],
        recommendations=recommendations,
        content_text=content_text,
        language=language,
        generated_at=generated_at.strftime("%d.%m.%Y %H:%M"),
    )


@router.post("/", response_model=ProposalResponse)
async def create_proposal(
    *,
    db: Session = Depends(deps.get_db),
    proposal_in: ProposalCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """Создать коммерческое предложение для лида."""
    # Проверяем, что лид принадлежит пользователю
    lead = (
        db.query(Lead)
        .join(Lead.search)
        .filter(Lead.id == proposal_in.lead_id, Lead.search.has(user_id=current_user.id))
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Вызываем HoReCa API для генерации КП
    horeca = _get_horeca_client()
    lead_data = {
        "name": lead.name,
        "address": lead.address,
        "rating": lead.rating,
        "review_count": lead.review_count,
        "pain_points": lead.pain_points or [],
        "last_negative_review_text": lead.last_negative_review_text,
    }

    try:
        proposal_data = await horeca.generate_proposal(
            lead_data=lead_data,
            language=proposal_in.language,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"HoReCa API error: {exc}",
        )

    content_text = proposal_data.get("content_text", "")
    recommendations = proposal_data.get("recommendations", [])
    now = datetime.utcnow()

    # Рендерим HTML и генерируем PDF
    content_html = _render_proposal_html(
        lead=lead,
        content_text=content_text,
        recommendations=recommendations,
        language=proposal_in.language,
        generated_at=now,
    )

    # Временно создаём запись без pdf_url, чтобы получить proposal_id
    proposal = Proposal(
        lead_id=lead.id,
        user_id=current_user.id,
        language=proposal_in.language,
        content_text=content_text,
        recommendations=recommendations,
        status=ProposalStatus.GENERATED,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    # Генерируем PDF
    pdf_gen = PDFGenerator()
    pdf_path = pdf_gen.generate_pdf(
        proposal_id=proposal.id,
        content_html=content_html,
        output_dir=PDF_OUTPUT_DIR,
    )

    # Сохраняем pdf_url как публичный путь
    proposal.pdf_url = f"/api/proposals/{proposal.id}/pdf"
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    return proposal


@router.get("/", response_model=List[ProposalResponse])
def read_proposals(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Список КП текущего пользователя."""
    proposals = (
        db.query(Proposal)
        .filter(Proposal.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return proposals


@router.get("/{proposal_id}", response_model=ProposalResponse)
def read_proposal(
    *,
    db: Session = Depends(deps.get_db),
    proposal_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    """Детали коммерческого предложения."""
    proposal = (
        db.query(Proposal)
        .filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
        .first()
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.get("/{proposal_id}/pdf")
def download_proposal_pdf(
    *,
    db: Session = Depends(deps.get_db),
    proposal_id: int,
    current_user: User = Depends(deps.get_current_user),
):
    """Скачать PDF коммерческого предложения."""
    proposal = (
        db.query(Proposal)
        .filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
        .first()
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    pdf_path = os.path.join(PDF_OUTPUT_DIR, f"proposal_{proposal_id}.pdf")
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"proposal_{proposal_id}.pdf",
    )


@router.patch("/{proposal_id}/status", response_model=ProposalResponse)
def update_proposal_status(
    *,
    db: Session = Depends(deps.get_db),
    proposal_id: int,
    status_in: ProposalStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
):
    """Обновить статус коммерческого предложения."""
    proposal = (
        db.query(Proposal)
        .filter(Proposal.id == proposal_id, Proposal.user_id == current_user.id)
        .first()
    )
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal.status = status_in.status
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal
