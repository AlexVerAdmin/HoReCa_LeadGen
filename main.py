import os
import click
import logging
import csv
import json
from datetime import datetime
from dotenv import load_dotenv

from src.scout import GooglePlacesScout
from src.scorer import LeadScorer
from src.database import init_db, get_session
from src.models import Lead, LeadStatus

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LeadGenCLI")

load_dotenv()

@click.group()
def cli():
    """LeadGen Scout CLI - инструмент для поиска и квалификации HoReCa лидов."""
    pass

@cli.command()
def init():
    """Инициализировать базу данных."""
    click.echo("Инициализация базы данных...")
    init_db()
    click.echo("Готово.")

@cli.command(name='init-db')
def init_db_cmd():
    """Инициализировать базу данных (alias для init)."""
    click.echo("Инициализация базы данных...")
    init_db()
    click.echo("Готово.")

@cli.command()
@click.option('--lat', type=float, required=True, help='Широта центра поиска.')
@click.option('--lon', type=float, required=True, help='Долгота центра поиска.')
@click.option('--radius', type=int, default=5000, help='Радиус поиска в метрах (по умолчанию 5000).')
@click.option('--category', type=str, default='restaurant', help='Категория для поиска (по умолчанию restaurant).')
def search(lat, lon, radius, category):
    """Поиск и квалификация лидов по координатам."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        click.echo("Ошибка: GOOGLE_PLACES_API_KEY не задан в .env файле.", err=True)
        return

    scout = GooglePlacesScout(api_key)
    scorer = LeadScorer()
    session = get_session()

    click.echo(f"Начинаю поиск в радиусе {radius}м вокруг ({lat}, {lon})...")
    
    try:
        places = scout.search_nearby(lat, lon, radius, [category])
        click.echo(f"Найдено мест: {len(places)}")

        qualified_count = 0
        added_count = 0

        for place in places:
            place_id = place.get('place_id')
            if not place_id:
                continue

            # Проверяем, есть ли уже такой лид в БД
            existing_lead = session.query(Lead).filter(Lead.google_place_id == place_id).first()
            if existing_lead:
                continue

            # Получаем подробности
            details = scout.get_place_details(place_id)
            if not details:
                continue

            # Скоринг
            if scorer.is_qualified(details):
                qualified_count += 1
                
                # Создаем лид
                neg_review = scorer.analyze_reviews(details.get('reviews', []))
                
                new_lead = Lead(
                    google_place_id=place_id,
                    name=details.get('name'),
                    address=details.get('formatted_address'),
                    phone=details.get('formatted_phone_number'),
                    website=details.get('website'),
                    rating=details.get('rating'),
                    review_count=details.get('user_ratings_total'),
                    last_negative_review_text=neg_review,
                    status=LeadStatus.QUALIFIED
                )
                
                try:
                    session.add(new_lead)
                    session.commit()
                    added_count += 1
                    logger.info(f"Добавлен новый лид: {new_lead.name}")
                except Exception as e:
                    session.rollback()
                    logger.error(f"Ошибка при сохранении лида {details.get('name')}: {e}")

        click.echo(f"Обработка завершена.")
        click.echo(f"Результаты: Квалифицировано: {qualified_count}, Добавлено в БД: {added_count}")

    except Exception as e:
        click.echo(f"Произошла ошибка во время поиска: {e}", err=True)
    finally:
        session.close()

@cli.command()
@click.option('--format', type=click.Choice(['csv', 'json']), default='csv', help='Формат экспорта.')
@click.option('--status', type=click.Choice([s.value for s in LeadStatus]), help='Фильтр по статусу.')
def export(format, status):
    """Экспорт лидов из базы данных."""
    session = get_session()
    query = session.query(Lead)
    
    if status:
        query = query.filter(Lead.status == status)
    
    leads = query.all()
    if not leads:
        click.echo("Нет лидов для экспорта.")
        return

    filename = f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
    
    try:
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Address', 'Phone', 'Website', 'Rating', 'Reviews', 'Status', 'Negative Review'])
                for lead in leads:
                    writer.writerow([
                        lead.google_place_id, lead.name, lead.address, lead.phone, 
                        lead.website, lead.rating, lead.review_count, lead.status.value,
                        lead.last_negative_review_text
                    ])
        else:
            data = []
            for lead in leads:
                data.append({
                    'place_id': lead.google_place_id,
                    'name': lead.name,
                    'address': lead.address,
                    'phone': lead.phone,
                    'website': lead.website,
                    'rating': lead.rating,
                    'review_count': lead.review_count,
                    'status': lead.status.value,
                    'negative_review': lead.last_negative_review_text
                })
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        click.echo(f"Экспортировано {len(leads)} лидов в файл {filename}")
    except Exception as e:
        click.echo(f"Ошибка при экспорте: {e}", err=True)
    finally:
        session.close()

@cli.command()
def stats():
    """Показать статистику по базе данных."""
    session = get_session()
    try:
        total = session.query(Lead).count()
        click.echo(f"Общее количество лидов: {total}")
        
        for status in LeadStatus:
            count = session.query(Lead).filter(Lead.status == status).count()
            click.echo(f"  {status.value}: {count}")
    finally:
        session.close()

if __name__ == '__main__':
    cli()
