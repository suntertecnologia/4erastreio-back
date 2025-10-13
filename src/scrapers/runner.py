import importlib
from .scrapper_data_model import ScraperResponse

SCRAPER_MAPPING = {
    "braspress": "src.scrapers.braspress_scraper.rastrear_braspress",
    "accert": "src.scrapers.accert_scraper.rastrear_accert",
    "jamef": "src.scrapers.jamef_scraper.rastrear_jamef",
}

async def run_scraper(transportadora: str, numero_nf: str, cnpj_destinatario: str) -> ScraperResponse:
    if transportadora not in SCRAPER_MAPPING:
        raise ValueError(f"Scraper for '{transportadora}' not found.")

    module_path, function_name = SCRAPER_MAPPING[transportadora].rsplit('.', 1)
    
    try:
        module = importlib.import_module(module_path)
        scraper_function = getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import scraper function {function_name} from {module_path}: {e}")

    return await scraper_function(cnpj=cnpj_destinatario, nota_fiscal=numero_nf)
