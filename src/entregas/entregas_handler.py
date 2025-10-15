from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.scrapers import runner
from src.configs.logger_config import logger
from datetime import datetime


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


def scrap_and_save(scrap_request: entregas_models.EntregaScrapRequest, user_id: int):
    db: Session = database.SessionLocal()
    try:
        logger.info(
            f"Starting scraping for {scrap_request.transportadora} - NF {scrap_request.numero_nf}"
        )

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

            if existing_entrega:
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
                        update_data = entregas_models.EntregaUpdate(
                            status=scraped_data["historico"][0]["status"]
                        )
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
                    status=(
                        scraped_data["historico"][0]["status"]
                        if scraped_data.get("historico")
                        else "Desconhecido"
                    ),
                    previsao_entrega=info.get("previsao_entrega"),
                    historico=scraped_data.get("historico"),
                )
                entregas_crud.create_entrega(
                    db=db, entrega=entrega_data, user_id=user_id
                )
                logger.info("New delivery created.")

        else:
            logger.error(
                f"Scraping failed for {scrap_request.transportadora} - NF {scrap_request.numero_nf}: {scraped_data.get('erro')}"
            )

    except Exception as e:
        logger.error(
            f"An error occurred during the scrap and save process: {e}", exc_info=True
        )
    finally:
        db.close()
