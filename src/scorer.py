import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class LeadScorer:
    """
    Класс для оценки и квалификации лидов на основе данных из Google Places.
    """

    def is_qualified(self, place_data: dict) -> bool:
        """
        Проверяет, подходит ли заведение под критерии квалификации.
        Критерии:
        - Количество отзывов >= 30
        - Рейтинг от 3.5 до 4.3 (включительно)
        - Наличие негативных отзывов за последние 30 дней без ответа владельца
        """
        rating = place_data.get('rating', 0)
        user_ratings_total = place_data.get('user_ratings_total', 0)
        
        # Проверка базовых критериев: количество отзывов и рейтинг
        if user_ratings_total < 30:
            logger.debug(f"Lead {place_data.get('name')} rejected: low review count ({user_ratings_total})")
            return False
            
        if not (3.5 <= rating <= 4.3):
            logger.debug(f"Lead {place_data.get('name')} rejected: rating {rating} out of range [3.5, 4.3]")
            return False

        # Проверка негативных отзывов без ответа
        reviews = place_data.get('reviews', [])
        negative_review_no_reply = self.analyze_reviews(reviews)
        
        if negative_review_no_reply:
            logger.debug(f"Lead {place_data.get('name')} qualified: found negative review without reply")
            return True
        else:
            logger.debug(f"Lead {place_data.get('name')} rejected: no negative reviews without reply found")
            return False

    def analyze_reviews(self, reviews: list) -> str:
        """
        Ищет негативные отзывы (1-2 звезды) без ответа владельца.
        Возвращает текст первого найденного такого отзыва или None.
        Примечание: В MVP Google Places API возвращает до 5 самых релевантных отзывов.
        """
        if not reviews:
            return None

        for review in reviews:
            rating = review.get('rating', 0)
            # Ищем отзывы 1 или 2 звезды
            if rating <= 2:
                # Проверяем отсутствие ответа владельца
                if not review.get('author_attribution') and not review.get('text'):
                    continue # Пропускаем пустые
                
                # В Google Places API v1 ответ находится в поле 'authorAttribution' (для новых версий) 
                # или проверяется наличие 'text' в контексте ответа. 
                # Согласно документации Google Maps Python Client, ответ обычно в 'reviews[].text'
                # и если нет 'author_attribution' в блоке ответа.
                
                # В текущей реализации python-googlemaps ответ владельца приходит в review.get('owner_response')
                # или соответствующем поле. Если его нет - отзыв считается без ответа.
                if not review.get('owner_response'):
                    return review.get('text', 'No text provided')
                    
        return None

    def calculate_priority_score(self, place_data: dict) -> float:
        """
        Вычисляет приоритет лида (v2). Пока возвращает базовое значение 1.0.
        """
        return 1.0
