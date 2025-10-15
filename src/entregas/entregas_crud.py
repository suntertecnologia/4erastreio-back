from sqlalchemy.orm import Session
from src.db import models
from src.entregas import entregas_models


def get_entrega(db: Session, entrega_id: int):
    return db.query(models.Entrega).filter(models.Entrega.id == entrega_id).first()


def get_entrega_by_tracking_info(
    db: Session, transportadora: str, numero_nf: str, cnpj_destinatario: str
):
    return (
        db.query(models.Entrega)
        .filter(
            models.Entrega.transportadora == transportadora,
            models.Entrega.numero_nf == numero_nf,
            models.Entrega.cnpj_destinatario == cnpj_destinatario,
        )
        .first()
    )


def create_entrega(db: Session, entrega: entregas_models.EntregaCreate, user_id: int):
    db_entrega = models.Entrega(**entrega.dict(), criado_por_id=user_id)
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)
    return db_entrega


def update_entrega(
    db: Session, entrega_id: int, entrega: entregas_models.EntregaUpdate, user_id: int
):
    db_entrega = get_entrega(db, entrega_id)
    if not db_entrega:
        return None

    update_data = entrega.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entrega, key, value)

    db_entrega.atualizado_por_id = user_id
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)
    return db_entrega
