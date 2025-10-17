from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# --- Scraper Configurations ---
SCRAPER_URLS = {
    "accert": "https://cliente.accertlogistica.com.br/rastreamento",
    "jamef": "https://www.jamef.com.br/#rastrear-carga",
    "braspress": "https://www.braspress.com/",
    "viaverde": "http://viaverde.supplytrack.com.br/",
}

BROWSER_CONFIG = {
    "headless": False,  # Mude para False para ver o navegador em ação
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "viewport": {"width": 1280, "height": 800},
}

TIMEOUTS = {
    "navigation": 30000,  # 30 segundos para navegação de página
    "element_search": 10000,  # 10 segundos para encontrar um elemento
    "page_load": 30000,  # 30 segundos para carregar uma página
    "selector_wait": 30000,  # 30 segundos para carregar uma página
    "element_wait": 30000,  # 30 segundos para carregar uma página
    "Brasspress_wait": 60000,
}

SCREENSHOT_ENABLED = True  # Habilita/desabilita a captura de tela em caso de erro
SCREENSHOT_DIR = "debug_screenshots"  # Diretório para salvar as capturas de tela

# ------------------

# --- Orchestrator Configurations ---
ORCHESTRATOR_USER_EMAIL = "shrekshrugers@shrekshrugers.com"
ORCHESTRATOR_USER_PASSWORD = "123"
TENTATIVAS_MAXIMAS = 3
DELAY_ENTRE_TENTATIVAS_SEGUNDOS = 5
CAMINHO_PLANILHA_ENTREGAS = "entregas.xlsx"
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT_SCRAPING = f"{BASE_URL}/entrega/scrap"
ENDPOINT_NOTIFICACAO = f"{BASE_URL}/notification/send-notifications"

# --- Proxy Configurations ---
# WARNING: Using free proxies is generally unreliable, slow, and can pose security risks.
# They are often short-lived and may lead to frequent blocking or data integrity issues.
# For robust scraping, consider using paid proxy services.
BRASPRESS_PROXIES = [
    # Add your Braspress proxies here, e.g., "http://user:pass@host:port"
    # Example with authentication: "http://username:password@host:port"
]
