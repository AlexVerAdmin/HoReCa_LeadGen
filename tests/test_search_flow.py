import sys
import os
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import User, Search, Lead
from src.services.search_service import SearchService
import asyncio
import pytest

@pytest.mark.asyncio
async def test_search():
    db: Session = SessionLocal()
    try:
        # 1. Берем существующего пользователя (админа)
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            print("Admin user not found. Please run create_admin.py first.")
            return

        print(f"Testing search for user: {user.email}")
        
        # 2. Инициализируем сервис
        search_service = SearchService(db)
        
        # 3. Запускаем поиск (Берн, координаты центра)
        # 52.5200, 13.4050 - Berlin center
        lat, lon = 52.5200, 13.4050
        radius = 1000
        place_types = ["restaurant"]
        
        print(f"Executing search: lat={lat}, lon={lon}, radius={radius}")
        
        search_record = await search_service.execute_search(
            user_id=user.id,
            lat=lat,
            lon=lon,
            radius=radius,
            place_types=place_types
        )
        
        print(f"Search completed with status: {search_record.status}")
        print(f"Total found: {search_record.total_found}")
        print(f"Qualified count: {search_record.qualified_count}")
        
        # 4. Проверяем лиды
        leads = db.query(Lead).filter(Lead.search_id == search_record.id).all()
        print(f"Leads in DB for this search: {len(leads)}")
        for lead in leads:
            print(f"- Lead: {lead.name}, Rating: {lead.rating}, Reviews: {lead.review_count}, Status: {lead.status}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_search())
