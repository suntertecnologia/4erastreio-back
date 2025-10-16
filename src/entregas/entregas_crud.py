from sqlalchemy.orm import Session
from src.db import models
from src.entregas import entregas_models
from datetime import datetime


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


def get_entrega_by_transportadora_and_nf(
    db: Session, transportadora: str, numero_nf: str
):
    return (
        db.query(models.Entrega)
        .filter(
            models.Entrega.transportadora == transportadora,
            models.Entrega.numero_nf == numero_nf,
        )
        .first()
    )


def create_entrega(db: Session, entrega: entregas_models.EntregaCreate, user_id: int):
    status = "em andamento"
    if entrega.historico:
        for movimento in entrega.historico:
            if "entregue" in movimento.get("status", "").lower():
                status = "entregue"
                break

    db_entrega = models.Entrega(
        transportadora=entrega.transportadora,
        codigo_rastreio=entrega.codigo_rastreio,
        numero_nf=entrega.numero_nf,
        cliente=entrega.cliente,
        cnpj_destinatario=entrega.cnpj_destinatario,
        status=status,
        previsao_entrega_inicial=entrega.previsao_entrega_inicial,
        previsao_entrega=entrega.previsao_entrega,
        criado_por_id=user_id,
    )
    db.add(db_entrega)
    db.commit()
    db.refresh(db_entrega)

    if entrega.historico:
        for movimento_data in entrega.historico:
            local = movimento_data.get("local")
            localizacao_str = (
                f"{local['cidade']} - {local['estado']}" if local else None
            )
            dt_movimento_str = movimento_data.get("timestamp")
            dt_movimento = (
                datetime.fromisoformat(dt_movimento_str) if dt_movimento_str else None
            )
            db_movimentacao = models.EntregaMovimentacao(
                movimento=movimento_data["status"],
                dt_movimento=dt_movimento,
                localizacao=localizacao_str,
                detalhes=movimento_data.get("detalhes"),
                entrega_id=db_entrega.id,
                criado_por_id=user_id,
            )
            db.add(db_movimentacao)
        db.commit()

    create_movimentacao_notificacao(db, db_entrega.id)

    return db_entrega


def add_movimentacoes_to_entrega(
    db: Session, entrega_id: int, historico: list, user_id: int
):
    for movimento_data in historico:
        local = movimento_data.get("local")
        localizacao_str = f"{local['cidade']} - {local['estado']}" if local else None
        dt_movimento_str = movimento_data.get("timestamp")
        dt_movimento = (
            datetime.fromisoformat(dt_movimento_str) if dt_movimento_str else None
        )
        db_movimentacao = models.EntregaMovimentacao(
            movimento=movimento_data["status"],
            dt_movimento=dt_movimento,
            localizacao=localizacao_str,
            detalhes=movimento_data.get("detalhes"),
            entrega_id=entrega_id,
            criado_por_id=user_id,
        )
        db.add(db_movimentacao)
    db.commit()


def create_movimentacao_notificacao(db: Session, entrega_id: int):
    db_movimentacao_notificacao = models.MovimentacaoNotificacao(
        entrega_id=entrega_id,
    )
    db.add(db_movimentacao_notificacao)
    db.commit()


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
