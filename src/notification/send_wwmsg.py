import requests
import json
import os
from dotenv import load_dotenv
from ..configs.logger_config import logger


# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
API_KEY = os.getenv("API_KEY")
RECIPIENT_NUMBER = os.getenv("RECIPIENT_NUMBER")

# Monta a URL completa do endpoint
url = f"{EVOLUTION_API_URL}/message/sendTemplate/{INSTANCE_NAME}"

# Define os headers da requisição
headers = {"Content-Type": "application/json", "apikey": API_KEY}

# Define o corpo (payload) da requisição
payload = {
    "number": RECIPIENT_NUMBER,
    "templateMessage": {
        "text": "Olá! Confira nosso novo site para mais informações.",
        "footer": "Clique no botão abaixo",
        "templateButtons": [
            {
                "index": 1,
                "urlButton": {
                    "displayText": "Acessar sistema",
                    "url": "https://www.google.com",  # O link que o botão vai abrir
                },
            }
        ],
    },
}

try:
    # Faz a requisição POST
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)

    # Verifica o status da resposta
    response.raise_for_status()  # Lança um erro para status HTTP 4xx/5xx

    # Imprime a resposta da API em caso de sucesso
    logger.info(f"Mensagem enviada com sucesso. Reposta: {response.json()}")

except requests.exceptions.HTTPError as errh:
    logger.info(f"Erro HTTP: {errh}")
    logger.info(f"Corpo da resposta: {response.text}")
except requests.exceptions.ConnectionError as errc:
    logger.info(f"Erro de Conexão: {errc}")
except requests.exceptions.Timeout as errt:
    logger.info(f"Erro de Timeout: {errt}")
except requests.exceptions.RequestException as err:
    logger.info(f"Erro desconhecido: {err}")
