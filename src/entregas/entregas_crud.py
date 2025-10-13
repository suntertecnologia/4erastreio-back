from sqlalchemy.orm import Session, joinedload
from src.db import models
from src.entregas import entregas_models

def get_entrega_by_tracking_info(db: Session, transportadora: str, numero_nf: str, cnpj_destinatario: str):
    return db.query(models.Entrega).options(joinedload(models.Entrega.movimentacoes)).filter(
        models.Entrega.transportadora == transportadora,
        models.Entrega.numero_nf == numero_nf,
        models.Entrega.cnpj_destinatario == cnpj_destinatario
    ).first()

def create_entrega(db: Session, entrega: entregas_models.EntregaCreate, user_id: int):
    existing_entrega = db.query(models.Entrega).filter(
        models.Entrega.transportadora == entrega.transportadora,
        models.Entrega.numero_nf == entrega.numero_nf
    ).first()
    if existing_entrega:
        raise ValueError("Entrega with the same transportadora and numero_nf already exists.")

    db_entrega = models.Entrega(
        **entrega.dict(exclude={"movimentacoes"}),
        criado_por_id=user_id,
        previsao_entrega_inicial=entrega.previsao_entrega
    )
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)

    for movimentacao in entrega.movimentacoes:
        db_movimentacao = models.EntregaMovimentacao(
            **movimentacao.dict(),
            entrega_id=db_entrega.id,
            criado_por_id=user_id
        )
        db.add(db_movimentacao)
    
    db.commit()
    db.refresh(db_entrega)
    return db_entrega
