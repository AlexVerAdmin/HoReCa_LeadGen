"""
Тестовый скрипт для проверки моделей БД.
Проверяет создание пользователя, поиска, лида и предложения.
"""

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import (
    Base,
    User,
    UserRole,
    UserSettings,
    Search,
    SearchStatus,
    Lead,
    LeadStatus,
    Proposal,
    ProposalStatus,
)


def test_models():
    """Тест создания и связывания моделей."""
    
    # Подключение к БД
    engine = create_engine("sqlite:///leadgen.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n=== Тест 1: Создание пользователя ===")
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here",
            role=UserRole.AGENT,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print(f"✓ Создан пользователь: {user}")
        
        print("\n=== Тест 2: Создание настроек пользователя ===")
        settings = UserSettings(
            user_id=user.id,
            ui_language="en",
            proposal_language="de",
            default_radius=5000,
            default_place_types=["restaurant", "cafe"],
        )
        session.add(settings)
        session.commit()
        print(f"✓ Созданы настройки: {settings}")
        
        print("\n=== Тест 3: Создание поиска ===")
        search = Search(
            user_id=user.id,
            latitude=52.520008,
            longitude=13.404954,
            radius=5000,
            place_types=["restaurant"],
            query_string="Italian restaurant",
            status=SearchStatus.COMPLETED,
            total_found=10,
            qualified_count=3,
        )
        session.add(search)
        session.commit()
        print(f"✓ Создан поиск: {search}")
        
        print("\n=== Тест 4: Создание лида ===")
        lead = Lead(
            search_id=search.id,
            google_place_id="ChIJtest123",
            name="Test Restaurant",
            address="Test Street 1, Berlin",
            phone="+49301234567",
            website="https://test-restaurant.de",
            rating=4.2,
            review_count=150,
            last_negative_review_text="Service was slow",
            pain_points=["low_rating", "negative_reviews"],
            status=LeadStatus.QUALIFIED,
        )
        session.add(lead)
        session.commit()
        print(f"✓ Создан лид: {lead}")
        
        print("\n=== Тест 5: Создание предложения ===")
        proposal = Proposal(
            lead_id=lead.id,
            user_id=user.id,
            language="de",
            content_text="Test proposal content",
            recommendations=["Improve response rate", "Boost rating"],
            status=ProposalStatus.DRAFT,
        )
        session.add(proposal)
        session.commit()
        print(f"✓ Создано предложение: {proposal}")
        
        print("\n=== Тест 6: Проверка relationships ===")
        # Перезагрузка объектов для проверки relationships
        session.refresh(user)
        session.refresh(search)
        session.refresh(lead)
        
        print(f"✓ Пользователь {user.username} имеет {len(user.searches)} поисков")
        print(f"✓ Поиск {search.id} имеет {len(search.leads)} лидов")
        print(f"✓ Лид {lead.name} связан с поиском {lead.search.id}")
        print(f"✓ Лид {lead.name} имеет {len(lead.proposals)} предложений")
        
        print("\n=== ✓ Все тесты пройдены успешно! ===")
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    test_models()
