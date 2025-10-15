from sqlalchemy.orm import Session
from src.db import models


def get_pending_notifications(db: Session):
    return (
        db.query(models.MovimentacaoNotificacao)
        .filter(models.MovimentacaoNotificacao.status == "nao notificado")
        .all()
    )


def create_notification_log(
    db: Session, detalhes: str, status: str, entrega_id: int, user_id: int
):
    db_log = models.NotificacaoLog(
        detalhes=detalhes, status=status, entrega_id=entrega_id, criado_por_id=user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def update_movimentacao_notificacao(
    db: Session, movimentacao_id: int, notificacao_id: int, status: str
):
    db_movimentacao = (
        db.query(models.MovimentacaoNotificacao)
        .filter(models.MovimentacaoNotificacao.id == movimentacao_id)
        .first()
    )
    if db_movimentacao:
        db_movimentacao.notificacao_id = notificacao_id
        db_movimentacao.status = status
        db.commit()
        db.refresh(db_movimentacao)
    return db_movimentacao
