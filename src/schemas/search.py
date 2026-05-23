from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from src.models import SearchStatus

class SearchCreate(BaseModel):
    latitude: float = Field(..., description="Широта центра поиска")
    longitude: float = Field(..., description="Долгота центра поиска")
    radius: int = Field(5000, description="Радиус поиска в метрах")
    place_types: List[str] = Field(default=["restaurant"], description="Типы заведений (Google Places types)")
    query_string: Optional[str] = Field(None, description="Строка поиска (опционально)")

class SearchResponse(BaseModel):
    id: int
    status: SearchStatus
    total_found: int
    qualified_count: int
    lat: float
    lon: float
    radius: int
    place_types: List[str]
    query_string: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
