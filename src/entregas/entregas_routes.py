import uuid
from fastapi import Depends, HTTPException, status, BackgroundTasks, APIRouter
from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario, ScrapingTask  # Import ScrapingTask
from src.entregas.entregas_handler import scrap_and_save

router = APIRouter()


@router.post("/scrap", status_code=status.HTTP_202_ACCEPTED)
def scrap_entrega(
    scrap_request: entregas_models.EntregaScrapRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),  # Add db session
    current_user: Usuario = Depends(get_current_user),
):
    task_id = str(uuid.uuid4())
    # Create a pending task in the database
    db_task = ScrapingTask(task_id=task_id, status="PENDING")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    background_tasks.add_task(scrap_and_save, scrap_request, current_user.id, task_id)
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
    task = db.query(ScrapingTask).filter(ScrapingTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scraping task not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "entrega_id": task.entrega_id,
        "error_message": task.error_message,
    }


@router.post(
    "/", response_model=entregas_models.EntregaOut, status_code=status.HTTP_201_CREATED
)
def create_entrega(
    entrega: entregas_models.EntregaCreate,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        return entregas_crud.create_entrega(
            db=db, entrega=entrega, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{entrega_id}", response_model=entregas_models.EntregaOut)
def get_entrega(
    entrega_id: int,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    entrega = entregas_crud.get_entrega(db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega not found")
    return entrega


@router.put("/{entrega_id}", response_model=entregas_models.EntregaOut)
def update_entrega(
    entrega_id: int,
    entrega: entregas_models.EntregaUpdate,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user),
):
    db_entrega = entregas_crud.update_entrega(
        db=db, entrega_id=entrega_id, entrega=entrega, user_id=current_user.id
    )
    if db_entrega is None:
        raise HTTPException(status_code=404, detail="Entrega not found")
    return db_entrega
