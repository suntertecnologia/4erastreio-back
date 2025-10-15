from fastapi import FastAPI
from src.auth import auth_routes
from src.entregas import entregas_routes
from src.db import models
from src.db.database import engine
from src.scrapers.scrapper_data_model import StandardizedDeliveryData
from src.configs.logger_config import logger

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth")
app.include_router(entregas_routes.router, prefix="/entrega")


@app.get("/")
def read_root():
    return {"message": "Welcome to the SunterCode Tracking API"}


@app.post("/receber_json")
def receber_json(data: StandardizedDeliveryData):
    """
    Recebe os dados de rastreamento em formato JSON padronizado.
    """
    logger.info(f"Dados recebidos via API: {data}")
    # Aqui você pode adicionar a lógica para salvar os dados no banco de dados
    return {"status": "sucesso", "dados_recebidos": data}
