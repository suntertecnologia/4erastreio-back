from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.auth.auth_handler import get_current_user
from src.db.models import Usuario

router = APIRouter()

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
