from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.scrapers import runner
from src.configs.logger_config import logger
from datetime import datetime
from src.db.models import ScrapingTask  # Import ScrapingTask


def get_movimento_tuple(movimento):
    if isinstance(movimento, dict):
        local = movimento.get("local")
        localizacao_str = f"{local['cidade']} - {local['estado']}" if local else None
        dt_movimento_str = movimento.get("timestamp")
        dt_movimento = (
            datetime.fromisoformat(dt_movimento_str) if dt_movimento_str else None
        )
        return (
            movimento.get("status"),
            dt_movimento,
            localizacao_str,
            movimento.get("detalhes"),
        )
    else:  # It's an EntregaMovimentacao object
        return (
            movimento.movimento,
            movimento.dt_movimento,
            movimento.localizacao,
            movimento.detalhes,
        )


def scrap_and_save(
    scrap_request: entregas_models.EntregaScrapRequest, user_id: int, task_id: str
):
    db: Session = database.SessionLocal()
    try:
        logger.info(
            f"Starting scraping for {scrap_request.transportadora} - NF {scrap_request.numero_nf} (Task ID: {task_id})"
        )
        # Update task status to IN_PROGRESS (optional, PENDING is fine for start)
        db_task = db.query(ScrapingTask).filter(ScrapingTask.task_id == task_id).first()
        if db_task:
            db_task.status = "IN_PROGRESS"
            db.add(db_task)
            db.commit()
            db.refresh(db_task)

        import asyncio

        scraped_data = asyncio.run(
            runner.run_scraper(
                transportadora=scrap_request.transportadora,
                numero_nf=scrap_request.numero_nf,
                cnpj_destinatario=scrap_request.cnpj_destinatario,
                credentials=scrap_request.credentials,
            )
        )

        if scraped_data and scraped_data.get("informacoes_gerais"):
            logger.info(
                f"Scraping successful for {scrap_request.transportadora} - NF {scrap_request.numero_nf}. Data: {scraped_data}"
            )

            info = scraped_data["informacoes_gerais"]
            existing_entrega = entregas_crud.get_entrega_by_transportadora_and_nf(
                db, info["transportadora"], info["numero_nf"]
            )

            entrega_id = None
            if existing_entrega:
                logger.info("Entrega já existe")
                entrega_id = existing_entrega.id
                # Delivery exists, check for new movements
                scraped_movimentos = set()
                if scraped_data.get("historico"):
                    scraped_movimentos = {
                        get_movimento_tuple(m) for m in scraped_data["historico"]
                    }

                db_movimentos = {
                    get_movimento_tuple(m) for m in existing_entrega.movimentacoes
                }

                if scraped_movimentos != db_movimentos:
                    # New movements found, update delivery
                    if scraped_data.get("historico"):
                        # This is not efficient, but it's the simplest way to update
                        entregas_crud.delete_movimentacoes_by_entrega_id(
                            db, existing_entrega.id
                        )
                        entregas_crud.add_movimentacoes_to_entrega(
                            db, existing_entrega.id, scraped_data["historico"], user_id
                        )
                        new_status = existing_entrega.status
                        if scraped_data.get("historico"):
                            has_entregue = any(
                                ("entregue" or "realizada")
                                in m.get("status", "").lower()
                                for m in scraped_data["historico"]
                            )
                            if has_entregue:
                                new_status = "entregue"
                            else:
                                new_status = scraped_data["historico"][0]["status"]

                        update_data = entregas_models.EntregaUpdate(status=new_status)
                        entregas_crud.update_entrega(
                            db, existing_entrega.id, update_data, user_id
                        )
                        entregas_crud.create_movimentacao_notificacao(
                            db, existing_entrega.id
                        )
                        logger.info(
                            f"Delivery {existing_entrega.id} updated with new movements."
                        )
                else:
                    logger.info(f"No new movements for delivery {existing_entrega.id}.")
            else:
                # Delivery does not exist, create it
                entrega_data = entregas_models.EntregaCreate(
                    transportadora=info["transportadora"],
                    codigo_rastreio=info["codigo_rastreio"],
                    numero_nf=info["numero_nf"],
                    cliente=info.get("destinatario"),
                    cnpj_destinatario=info.get("cnpj_destinatario"),
                    previsao_entrega=info.get("previsao_entrega"),
                    previsao_entrega_inicial=info.get("previsao_entrega"),
                    historico=scraped_data.get("historico"),
                )
                new_entrega = entregas_crud.create_entrega(
                    db=db, entrega=entrega_data, user_id=user_id
                )
                entrega_id = new_entrega.id
                logger.info("New delivery created.")

            # Update task status to SUCCESS
            if db_task:
                db_task.status = "SUCCESS"
                db_task.entrega_id = entrega_id
                db.add(db_task)
                db.commit()
                db.refresh(db_task)

        else:
            error_msg = f"Scraping failed for {scrap_request.transportadora} - NF {scrap_request.numero_nf}: {scraped_data.get('erro')}"
            logger.error(error_msg)
            if db_task:
                db_task.status = "FAILED"
                db_task.error_message = error_msg
                db.add(db_task)
                db.commit()
                db.refresh(db_task)

    except Exception as e:
        error_msg = f"An error occurred during the scrap and save process (Task ID: {task_id}): {e}"
        logger.error(error_msg, exc_info=True)
        if db_task:
            db_task.status = "FAILED"
            db_task.error_message = error_msg
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
    finally:
        db.close()
