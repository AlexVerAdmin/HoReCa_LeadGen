from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.api import deps
from src.schemas.lead import LeadResponse, LeadStatusUpdate
from src.models import User, Lead, LeadStatus

router = APIRouter()

@router.get("/", response_model=List[LeadResponse])
def read_leads(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    search_id: Optional[int] = None,
    status: Optional[LeadStatus] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Получает список лидов с фильтрацией.
    """
    query = db.query(Lead)
    
    # В MVP лиды привязаны к поискам, а поиски к юзерам.
    # Если мы хотим видеть только "свои" лиды:
    query = query.join(Lead.search).filter(Lead.search.has(user_id=current_user.id))
    
    if search_id:
        query = query.filter(Lead.search_id == search_id)
    if status:
        query = query.filter(Lead.status == status)
        
    leads = query.offset(skip).limit(limit).all()
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
def read_lead(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Получает детали лида.
    """
    lead = db.query(Lead).join(Lead.search).filter(
        Lead.id == lead_id, 
        Lead.search.has(user_id=current_user.id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(
    *,
    db: Session = Depends(deps.get_db),
    lead_id: int,
    status_in: LeadStatusUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Обновляет статус лида.
    """
    lead = db.query(Lead).join(Lead.search).filter(
        Lead.id == lead_id, 
        Lead.search.has(user_id=current_user.id)
    ).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    lead.status = status_in.status
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead
