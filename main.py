from src.scrapers.braspress_scraper import rastrear_braspress
from src.scrapers.jamef_scraper import rastrear_jamef
from src.scrapers.viaverde_scraper import rastrear_viaverde
from src.scrapers.accert_scraper import rastrear_accert
from src.config.logger_config import logger
import asyncio

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
        
# Test braspress (OK)
print(export_data("braspress","34.122.358/0001-09", "8231"))

# Test accert (BOM) 
# print(export_data("accert","11.173.954/0001-12", "15095"))

# # Test jamef (BOM)
# print(export_data("jamef","48.775.1910001-90", "1160274"))

# Test ViaVerde (BOM)
# print(export_data("viaverde","48.775.1910001-90", "118895"))