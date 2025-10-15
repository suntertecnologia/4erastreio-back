from .accert_scraper import AccertScraper
from .jamef_scraper import JamefScraper
from .braspress_scraper import BrasspressScraper
from .viaverde_scraper import ViaVerdeScraper

SCRAPERS = {
    "accert": AccertScraper,
    "jamef": JamefScraper,
    "braspress": BrasspressScraper,
    "viaverde": ViaVerdeScraper,
}


async def run_scraper(transportadora: str, numero_nf: str, cnpj_destinatario: str):
    """
    Dynamically selects and runs a scraper based on the transportadora name.
    """
    scraper_class = SCRAPERS.get(transportadora.lower())
    if not scraper_class:
        raise ValueError(f"Transportadora '{transportadora}' not supported.")

    scraper = scraper_class()
    return await scraper.execute(
        numero_nf=numero_nf, cnpj_destinatario=cnpj_destinatario
    )
