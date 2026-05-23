import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models import Search, SearchStatus, Lead, LeadStatus
from src.scout import GooglePlacesScout
from src.scorer import LeadScorer
from src.core.config import settings

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.scout = GooglePlacesScout(api_key=settings.GOOGLE_PLACES_API_KEY)
        self.scorer = LeadScorer()

    async def execute_search(self, user_id: int, lat: float, lon: float, 
                           radius: int, place_types: List[str], 
                           query_string: Optional[str] = None) -> Search:
        """
        Выполняет поиск заведений, оценивает их и сохраняет в БД.
        В MVP выполняется синхронно (или в background task).
        """
        # 1. Создать запись Search (PENDING)
        search_record = Search(
            user_id=user_id,
            latitude=lat,
            longitude=lon,
            radius=radius,
            place_types=place_types,
            query_string=query_string,
            status=SearchStatus.IN_PROGRESS
        )
        self.db.add(search_record)
        self.db.commit()
        self.db.refresh(search_record)

        try:
            # 2. Поиск мест через GooglePlacesScout
            # В MVP используем первый тип из списка для search_nearby
            categories = place_types if place_types else ["restaurant"]
            raw_places = self.scout.search_nearby(lat=lat, lon=lon, radius=radius, categories=categories)
            
            search_record.total_found = len(raw_places)
            qualified_count = 0

            for place in raw_places:
                place_id = place.get("place_id")
                if not place_id:
                    continue

                # Проверяем, существует ли уже такой лид в БД (чтобы не дублировать)
                existing_lead = self.db.query(Lead).filter(Lead.google_place_id == place_id).first()
                if existing_lead:
                    # Если лид уже есть, можем обновить его search_id или просто пропустить
                    # Для простоты MVP - просто привязываем к последнему поиску
                    existing_lead.search_id = search_record.id
                    qualified_count += 1
                    continue

                # Получаем детали места (отзывы и т.д.)
                details = self.scout.get_place_details(place_id)
                if not details:
                    continue

                # 3. Квалификация лида через LeadScorer
                if self.scorer.is_qualified(details):
                    negative_review = self.scorer.analyze_reviews(details.get("reviews", []))
                    
                    # Создаем лид
                    new_lead = Lead(
                        search_id=search_record.id,
                        google_place_id=place_id,
                        name=details.get("name"),
                        address=details.get("formatted_address"),
                        phone=details.get("formatted_phone_number"),
                        website=details.get("website"),
                        rating=details.get("rating"),
                        review_count=details.get("user_ratings_total"),
                        last_negative_review_text=negative_review,
                        pain_points=["No response to negative review"] if negative_review else [],
                        status=LeadStatus.NEW
                    )
                    self.db.add(new_lead)
                    qualified_count += 1

            # 4. Обновить Search (COMPLETED)
            search_record.qualified_count = qualified_count
            search_record.status = SearchStatus.COMPLETED
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error during search execution: {e}")
            search_record.status = SearchStatus.FAILED
            self.db.commit()

        return search_record
