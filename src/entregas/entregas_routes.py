from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session
from src.entregas import entregas_models, entregas_service
from src.db import database
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario

router = APIRouter()


@router.post("/scrap", status_code=status.HTTP_202_ACCEPTED)
def scrap_entrega(
    scrap_request: entregas_models.EntregaScrapRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    task_id = entregas_service.initiate_scraping(
        scrap_request, background_tasks, db, current_user.id
    )
    return {
        "message": "Scraping process initiated in the background.",
        "task_id": task_id,
    }


@router.get("/scrap/status/{task_id}")
def get_scraping_status(
    task_id: str,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return entregas_service.get_scraping_status(task_id, db)


@router.post(
    "/", response_model=entregas_models.EntregaOut, status_code=status.HTTP_201_CREATED
)
def create_entrega(
    entrega: entregas_models.EntregaCreate,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return entregas_service.create_new_entrega(entrega, db, current_user.id)


@router.get("/{entrega_id}", response_model=entregas_models.EntregaOut)
def get_entrega(
    entrega_id: int,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return entregas_service.get_entrega_details(entrega_id, db)


@router.put("/{entrega_id}", response_model=entregas_models.EntregaOut)
def update_entrega(
    entrega_id: int,
    entrega: entregas_models.EntregaUpdate,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return entregas_service.update_existing_entrega(
        entrega_id, entrega, db, current_user.id
    )
