from .accert_scraper import AccertScraper
from .jamef_scraper import JamefScraper
from .braspress_scraper import BrasspressScraper
from .viaverde_scraper import ViaVerdeScraper
from ..utils.normalizer_factory import get_normalizer
import os
from dotenv import load_dotenv

SCRAPERS = {
    "accert": AccertScraper,
    "jamef": JamefScraper,
    "braspress": BrasspressScraper,
    "viaverde": ViaVerdeScraper,
}


async def run_scraper(
    transportadora: str,
    numero_nf: str,
    cnpj_destinatario: str,
    credentials: dict = None,
):
    """
    Dynamically selects and runs a scraper and its normalizer.
    """
    load_dotenv()
    scraper_class = SCRAPERS.get(transportadora.lower())
    if not scraper_class:
        raise ValueError(f"Transportadora '{transportadora}' not supported.")

    scraper = scraper_class()
    normalizer_func = get_normalizer(transportadora)

    if transportadora.lower() == "viaverde":
        if credentials:
            raw_data = await scraper.execute(
                login=credentials["username"],
                senha=credentials["password"],
                n_rastreio=numero_nf,
            )
        else:
            raw_data = await scraper.execute(
                login=os.getenv("VIAVERDE_USER"),
                senha=os.getenv("VIAVERDE_PASSWORD"),
                n_rastreio=numero_nf,
            )
    else:
        raw_data = await scraper.execute(nota_fiscal=numero_nf, cnpj=cnpj_destinatario)

    if raw_data and raw_data.get("status") == "sucesso":
        return normalizer_func(raw_data["dados"], cnpj_destinatario, numero_nf)
    else:
        return raw_data
