import logging
import time
import googlemaps
from typing import List, Dict, Optional, Any

# Настройка логирования для модуля поиска
logger = logging.getLogger(__name__)

class GooglePlacesScout:
    """
    Класс для работы с Google Places API.
    Отвечает за поиск мест и получение детальной информации о них.
    """

    def __init__(self, api_key: str):
        """
        Инициализация клиента Google Maps.
        
        :param api_key: Ключ API Google Maps
        """
        if not api_key:
            logger.error("API Key не предоставлен.")
            raise ValueError("Google Places API key is required")
        
        self.client = googlemaps.Client(key=api_key)
        logger.info("GooglePlacesScout инициализирован.")

    def search_nearby(self, lat: float, lon: float, radius: int = 5000, 
                      categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Выполняет поиск мест поблизости с использованием Nearby Search.
        Поддерживает пагинацию через next_page_token.
        
        :param lat: Широта
        :param lon: Долгота
        :param radius: Радиус поиска в метрах
        :param categories: Список категорий (например, ['restaurant'])
        :return: Список найденных мест (результатов)
        """
        location = (lat, lon)
        # Если типы не указаны, используем 'restaurant' как категорию по умолчанию для HoReCa
        place_types = categories if categories else ['restaurant']
        
        all_results = []
        next_page_token = None
        
        logger.info(f"Начало поиска: loc=({lat}, {lon}), radius={radius}, types={place_types}")

        try:
            while True:
                # Согласно документации Google, при использовании next_page_token 
                # остальные параметры должны быть такими же или отсутствовать.
                if next_page_token:
                    # Google требует небольшой задержки перед использованием токена следующей страницы
                    time.sleep(2)
                    response = self.client.places_nearby(
                        page_token=next_page_token
                    )
                else:
                    # Первый запрос
                    # Мы можем передать только один type в places_nearby за раз для лучших результатов, 
                    # либо полагаться на keyword. Но ТЗ говорит про categories.
                    # googlemaps library позволяет передать type как строку.
                    response = self.client.places_nearby(
                        location=location,
                        radius=radius,
                        type=place_types[0] if place_types else None
                    )

                results = response.get('results', [])
                all_results.extend(results)
                
                logger.info(f"Получено {len(results)} результатов. Всего: {len(all_results)}")
                
                next_page_token = response.get('next_page_token')
                if not next_page_token:
                    break
                    
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Ошибка Google Places API: {e.status} - {e}")
            # В зависимости от статуса (OVER_QUERY_LIMIT, REQUEST_DENIED и т.д.) 
            # можно добавить специфичную обработку.
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при поиске: {e}")
            
        return all_results

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает детальную информацию о конкретном месте.
        Включает отзывы, часы работы, веб-сайт и номер телефона.
        
        :param place_id: Уникальный ID места в Google Places
        :return: Словарь с деталями или None в случае ошибки
        """
        fields = [
            'name', 'formatted_address', 'formatted_phone_number', 
            'website', 'rating', 'user_ratings_total', 'reviews', 
            'opening_hours', 'geometry', 'plus_code'
        ]
        
        logger.info(f"Запрос деталей для place_id: {place_id}")
        
        try:
            result = self.client.place(
                place_id=place_id,
                fields=fields,
                language='ru' # Предпочтительно на русском для локальных нужд
            )
            
            details = result.get('result')
            if not details:
                logger.warning(f"Детали для {place_id} не найдены.")
                return None
            
            return details
            
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"Ошибка API при получении деталей {place_id}: {e.status}")
        except Exception as e:
            logger.error(f"Ошибка при получении деталей {place_id}: {e}")
            
        return None
