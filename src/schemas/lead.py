from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from src.models import LeadStatus

class LeadResponse(BaseModel):
    id: int
    google_place_id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    last_negative_review_text: Optional[str] = None
    pain_points: Optional[List[str]] = None
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LeadStatusUpdate(BaseModel):
    status: LeadStatus = Field(..., description="Новый статус лида")
