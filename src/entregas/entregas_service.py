import uuid
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db.models import ScrapingTask
from src.entregas.entregas_handler import scrap_and_save


def initiate_scraping(
    scrap_request: entregas_models.EntregaScrapRequest,
    background_tasks: BackgroundTasks,
    db: Session,
    user_id: int,
):
    task_id = str(uuid.uuid4())
    db_task = ScrapingTask(task_id=task_id, status="PENDING")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    background_tasks.add_task(scrap_and_save, scrap_request, user_id, task_id)
    return task_id


def get_scraping_status(task_id: str, db: Session):
    task = db.query(ScrapingTask).filter(ScrapingTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scraping task not found")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "entrega_id": task.entrega_id,
        "error_message": task.error_message,
    }


def create_new_entrega(
    entrega: entregas_models.EntregaCreate, db: Session, user_id: int
):
    try:
        return entregas_crud.create_entrega(db=db, entrega=entrega, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


def get_entrega_details(entrega_id: int, db: Session):
    entrega = entregas_crud.get_entrega(db, entrega_id=entrega_id)
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega not found")
    return entrega


def update_existing_entrega(
    entrega_id: int, entrega: entregas_models.EntregaUpdate, db: Session, user_id: int
):
    db_entrega = entregas_crud.update_entrega(
        db=db, entrega_id=entrega_id, entrega=entrega, user_id=user_id
    )
    if db_entrega is None:
        raise HTTPException(status_code=404, detail="Entrega not found")
    return db_entrega
