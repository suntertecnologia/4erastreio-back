from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario
from src.scrapers.parsers import parse_scraped_data
from src.config.logger_config import logger

def scrap_and_save(scrap_request: entregas_models.EntregaScrapRequest, user_id: int):
    db: Session = database.SessionLocal()
    try:
        logger.info(f"Starting scraping for {scrap_request.transportadora} - NF {scrap_request.numero_nf}")
        
        import asyncio
        scraped_data = asyncio.run(runner.run_scraper(
            transportadora=scrap_request.transportadora,
            numero_nf=scrap_request.numero_nf,
            cnpj_destinatario=scrap_request.cnpj_destinatario
        ))

        if scraped_data["status"] == "sucesso":
            logger.info(f"Scraping successful for {scrap_request.transportadora} - NF {scrap_request.numero_nf}. Data: {scraped_data['dados']}")
            
            entrega_data = parse_scraped_data(
                transportadora=scrap_request.transportadora,
                scraped_data=scraped_data['dados'],
                scrap_request=scrap_request.dict()
            )
            
            entregas_crud.create_entrega(db=db, entrega=entrega_data, user_id=user_id)
            logger.info(f"Successfully saved scraped data for {scrap_request.transportadora} - NF {scrap_request.numero_nf}")
        else:
            logger.error(f"Scraping failed for {scrap_request.transportadora} - NF {scrap_request.numero_nf}: {scraped_data['erro']}")

    except Exception as e:
        logger.error(f"An error occurred during the scrap and save process: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/scrap", status_code=status.HTTP_202_ACCEPTED)
def scrap_entrega(
    scrap_request: entregas_models.EntregaScrapRequest,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user)
):
    background_tasks.add_task(scrap_and_save, scrap_request, current_user.id)
    return {"message": "Scraping process initiated in the background."}

@router.post("/", response_model=entregas_models.EntregaOut, status_code=status.HTTP_201_CREATED)
def create_entrega(
    entrega: entregas_models.EntregaCreate,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        return entregas_crud.create_entrega(db=db, entrega=entrega, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("/", response_model=entregas_models.EntregaOut)
def get_entrega(
    carrierName: str,
    invoiceNumber: str,
    cnpj_destinatario: str,
    db: Session = Depends(database.get_db),
    current_user: Usuario = Depends(get_current_user)
):
    entrega = entregas_crud.get_entrega_by_tracking_info(
        db,
        transportadora=carrierName,
        numero_nf=invoiceNumber,
        cnpj_destinatario=cnpj_destinatario
    )
    if not entrega:
        raise HTTPException(status_code=404, detail="Entrega not found")
    return entrega
