from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from src.api import deps
from src.schemas.search import SearchCreate, SearchResponse
from src.schemas.lead import LeadResponse
from src.models import User, Search
from src.services.search_service import SearchService

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def create_search(
    *,
    db: Session = Depends(deps.get_db),
    search_in: SearchCreate,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks
):
    """
    Создает новый поиск и запускает его в фоновом режиме.
    """
    # Создаем запись поиска в PENDING
    search_service = SearchService(db)
    
    # Мы запускаем выполнение поиска как фоновую задачу, 
    # чтобы не блокировать API ответ
    # Сначала создаем запись в БД
    from src.models import SearchStatus
    search_record = Search(
        user_id=current_user.id,
        latitude=search_in.latitude,
        longitude=search_in.longitude,
        radius=search_in.radius,
        place_types=search_in.place_types,
        query_string=search_in.query_string,
        status=SearchStatus.PENDING
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)

    # Добавляем задачу в фон
    background_tasks.add_task(
        search_service.execute_search,
        user_id=current_user.id,
        lat=search_in.latitude,
        lon=search_in.longitude,
        radius=search_in.radius,
        place_types=search_in.place_types,
        query_string=search_in.query_string
    )

    return search_record

@router.get("/", response_model=List[SearchResponse])
def read_searches(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    維持: int = 100
):
    """
    Получает список поисков текущего пользователя.
    """
    searches = db.query(Search).filter(Search.user_id == current_user.id)\
        .offset(skip).limit(維持).all()
    return searches

@router.get("/{search_id}", response_model=SearchResponse)
def read_search(
    *,
    db: Session = Depends(deps.get_db),
    search_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Получает детали конкретного поиска.
    """
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return search

@router.get("/{search_id}/leads", response_model=List[LeadResponse])
def read_search_leads(
    *,
    db: Session = Depends(deps.get_db),
    search_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Получает лиды, найденные в рамках конкретного поиска.
    """
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    return search.leads

@router.delete("/{search_id}")
def delete_search(
    *,
    db: Session = Depends(deps.get_db),
    search_id: int,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Удаляет запись поиска.
    """
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")
    db.delete(search)
    db.commit()
    return {"status": "success"}
