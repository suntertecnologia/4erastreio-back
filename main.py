from src.scrapers.braspress_scraper import rastrear_braspress
from src.scrapers.jamef_scraper import rastrear_jamef
from src.scrapers.viaverde_scraper import rastrear_viaverde
from src.scrapers.accert_scraper import rastrear_accert
from src.utils.normalize_scrap_data import (
    normalize_braspress,
    normalize_jamef,
    normalize_viaverde,
    normalize_accert,
)
from src.configs.logger_config import logger
import asyncio
import requests
import json


def export_data(company: str, cnpj: str, nota_fiscal: str):
    async def get_tracking_data(company: str, cnpj: str, nota_fiscal: str):
        company = company.lower()
        raw_data = None
        match company:
            case "braspress":
                raw_data = await rastrear_braspress(cnpj, nota_fiscal)
                if raw_data and raw_data.get("status") == "sucesso":
                    return normalize_braspress(raw_data["dados"])
            case "jamef":
                raw_data = await rastrear_jamef(cnpj, nota_fiscal)
                if raw_data and raw_data.get("status") == "sucesso":
                    return normalize_jamef(raw_data["dados"])
            case "viaverde":
                raw_data = await rastrear_viaverde(
                    "pedidos.quatroestacoes", "4Edecoracoes", nota_fiscal
                )  # Login e senha fixos por enquanto
                if raw_data and raw_data.get("status") == "sucesso":
                    return normalize_viaverde(raw_data["dados"])
            case "accert":
                raw_data = await rastrear_accert(cnpj, nota_fiscal)
                if raw_data and raw_data.get("status") == "sucesso":
                    return normalize_accert(raw_data["dados"])
            case _:
                logger.error(f"Empresa '{company}' não suportada.")
                return None
        return raw_data  # Return raw_data if not successful

    return asyncio.run(get_tracking_data(company, cnpj, nota_fiscal))


def send_to_api(data):
    """
    Envia os dados para a API local.
    """
    try:
        response = requests.post(
            "http://localhost:8000/receber_json",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()  # Lança um erro para respostas HTTP 4xx/5xx
        logger.info(f"Dados enviados para a API com sucesso: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar dados para a API: {e}")
        logger.warning(
            "Certifique-se de que o servidor 'API/API_banco.py' está em execução."
        )
        return None


if __name__ == "__main__":
    # --- Exemplo de como usar ---
    # Altere os parâmetros conforme necessário
    tracking_data = export_data("viaverde", "48.775.1910001-90", "118895")
    print(tracking_data)

    # if tracking_data:
    #     # Envia os dados para a API
    #     send_to_api(tracking_data)

    # Você pode testar outras transportadoras também:
    # tracking_data_braspress = export_data("braspress","34.122.358/0001-09", "8231")
    # if tracking_data_braspress:
    #     send_to_api(tracking_data_braspress)
