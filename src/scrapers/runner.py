from .accert_scraper import AccertScraper
from .jamef_scraper import JamefScraper
from .braspress_scraper import BrasspressScraper
from .viaverde_scraper import ViaVerdeScraper
from ..utils.normalize_scrap_data import (
    normalize_accert,
    normalize_jamef,
    normalize_braspress,
    normalize_viaverde,
)
import os
from dotenv import load_dotenv

SCRAPERS = {
    "accert": AccertScraper,
    "jamef": JamefScraper,
    "braspress": BrasspressScraper,
    "viaverde": ViaVerdeScraper,
}

NORMALIZERS = {
    "accert": normalize_accert,
    "jamef": normalize_jamef,
    "braspress": normalize_braspress,
    "viaverde": normalize_viaverde,
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
    normalizer_func = NORMALIZERS.get(transportadora.lower())

    if not scraper_class or not normalizer_func:
        raise ValueError(f"Transportadora '{transportadora}' not supported.")

    scraper = scraper_class()

    if transportadora.lower() == "viaverde":
        if credentials:
            raw_data = await scraper.execute(
                login=credentials["username"],
                senha=credentials["password"],
                n_rastreio=numero_nf,
            )
        else:
            # Add default credentials from .env for viaverde
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
