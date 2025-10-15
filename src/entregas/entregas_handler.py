from sqlalchemy.orm import Session
from src.entregas import entregas_crud, entregas_models
from src.db import database
from src.scrapers import runner
from src.configs.logger_config import logger


def scrap_and_save(scrap_request: entregas_models.EntregaScrapRequest, user_id: int):
    db: Session = database.SessionLocal()
    message = ""
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
            )
        )

        if scraped_data and scraped_data.get("informacoes_gerais"):
            logger.info(
                f"Scraping successful for {scrap_request.transportadora} - NF {scrap_request.numero_nf}. Data: {scraped_data}"
            )

            info = scraped_data["informacoes_gerais"]
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
                previsao_entrega_inicial=info.get("previsao_entrega"),
            )

            entregas_crud.create_entrega(db=db, entrega=entrega_data, user_id=user_id)
            message = f"Scraping for {scrap_request.transportadora} - NF {scrap_request.numero_nf} completed successfully."
            logger.info(message)
        else:
            message = f"Scraping failed for {scrap_request.transportadora} - NF {scrap_request.numero_nf}: {scraped_data.get('erro')}"
            logger.error(message)

    except Exception as e:
        message = f"An error occurred during the scrap and save process: {e}"
        logger.error(message, exc_info=True)
    finally:
        db.close()
