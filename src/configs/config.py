from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# --- Scraper Configurations ---
SCRAPER_URLS = {
    "accert": "https://cliente.accertlogistica.com.br/rastreamento",
    "jamef": "https://www.jamef.com.br/#rastrear-carga",
    "braspress": "https://www.braspress.com/",
    "viaverde": "http://viaverde.supplytrack.com.br/",
}

BROWSER_CONFIG = {
    "headless": True,  # Mude para False para ver o navegador em ação
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "viewport": {"width": 1280, "height": 800},
}

TIMEOUTS = {
    "navigation": 30000,  # 30 segundos para navegação de página
    "element_search": 10000,  # 10 segundos para encontrar um elemento
    "page_load": 30000,  # 30 segundos para carregar uma página
    "selector_wait": 30000,  # 30 segundos para carregar uma página
    "element_wait": 30000,  # 30 segundos para carregar uma página
}

SCREENSHOT_ENABLED = False  # Habilita/desabilita a captura de tela em caso de erro
SCREENSHOT_DIR = "debug_screenshots"  # Diretório para salvar as capturas de tela

# ------------------
