from src.scrapers.braspress_scraper import rastrear_braspress
from src.scrapers.jamef_scraper import rastrear_jamef
from src.scrapers.viaverde_scraper import rastrear_viaverde
from src.scrapers.accert_scraper import rastrear_accert
from src.config.logger_config import logger
import asyncio
import requests
import json

def export_data(company: str,cnpj: str, nota_fiscal: str):
    async def get_tracking_data(company: str,cnpj: str, nota_fiscal: str):
        company = company.lower()
        match company:
            case "braspress":
                return await rastrear_braspress(cnpj, nota_fiscal)
            case "jamef":
                return await rastrear_jamef(cnpj, nota_fiscal)
            case "viaverde":
                return await rastrear_viaverde("pedidos.quatroestacoes","4Edecoracoes", nota_fiscal) # Login e senha fixos por enquanto
            case "accert":
                return await rastrear_accert(cnpj, nota_fiscal)
            case _:
                logger.error(f"Empresa '{company}' não suportada.")
                return None
    return asyncio.run(get_tracking_data(company,cnpj, nota_fiscal))

def send_to_api(data):
    """
    Envia os dados para a API local.
    """
    try:
        response = requests.post("http://localhost:8000/receber_json", data=json.dumps(data), headers={"Content-Type": "application/json"})
        response.raise_for_status()  # Lança um erro para respostas HTTP 4xx/5xx
        logger.info(f"Dados enviados para a API com sucesso: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar dados para a API: {e}")
        logger.warning("Certifique-se de que o servidor 'API/API_banco.py' está em execução.")
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