import asyncio
from ..config.logger_config import logger
from .base_scraper import BaseScraper
from .config import SCRAPER_URLS, TIMEOUTS
from .models import ScraperResponse


class AccertScraper(BaseScraper):
    """Scraper for ACCERT logistics tracking."""

    def __init__(self):
        super().__init__("accert")

    async def scrape(self, cnpj: str, nota_fiscal: str) -> ScraperResponse:
        """
        Realiza o web scraping do status de uma entrega no site da ACCERT.

        Args:
            cnpj: O CNPJ do remetente para a busca.
            nota_fiscal: O número da nota fiscal para a busca.

        Returns:
            ScraperResponse com as informações extraídas ou uma mensagem de erro.
        """
        page = await self.create_page()
        log_prefix = self._get_log_prefix(cnpj=cnpj, nota_fiscal=nota_fiscal)

        # 1. Acessar página de rastreamento
        logger.info(f"{log_prefix} - Acessando a página de rastreamento da ACCERT")
        await page.goto(SCRAPER_URLS["accert"], timeout=TIMEOUTS["page_load"])

        # 2. Preencher CNPJ
        logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
        await page.fill("#cnpjOrCpf", cnpj)

        # 3. Preencher Nota Fiscal
        logger.info(f"{log_prefix} - Preenchendo Nota Fiscal: {nota_fiscal}")
        nota_fiscal_input = await page.wait_for_selector('#notaFiscal', timeout=TIMEOUTS["selector_wait"])
        await nota_fiscal_input.fill(nota_fiscal)

        # 4. Clicar no botão de busca
        logger.info(f"{log_prefix} - Clicando no botão de busca")
        await page.click('button:has-text("Buscar encomendas")')

        # 5. Aguardar resultado e clicar em "Ver detalhes"
        logger.info(f"{log_prefix} - Aguardando resultados e clicando em Ver detalhes")
        elemento_chave = page.locator('span.text-base.font-semibold').first
        await elemento_chave.wait_for(timeout=TIMEOUTS["element_wait"])
        await page.click('button:has-text("Ver detalhes")')

        # 6. Extrair informações da entrega
        logger.info(f"{log_prefix} - Extraindo informações da entrega")
        seletor_container = ".border-separation"
        await page.wait_for_selector(seletor_container, timeout=TIMEOUTS["selector_wait"])
        detalhes_texto = await page.inner_text(seletor_container)

        # Retornar dados estruturados
        dados = {
            "detalhes": detalhes_texto.strip()
        }

        return self.success_response(dados)


async def rastrear_accert(cnpj: str, nota_fiscal: str) -> dict:
    """
    Função wrapper para manter compatibilidade com código existente.

    Args:
        cnpj: O CNPJ do remetente para a busca.
        nota_fiscal: O número da nota fiscal para a busca.

    Returns:
        Um dicionário com as informações extraídas ou uma mensagem de erro.
    """
    scraper = AccertScraper()
    return await scraper.execute(cnpj=cnpj, nota_fiscal=nota_fiscal)


async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com um CNPJ e Nota Fiscal reais para testar
    cnpj_exemplo = "11.173.954/0001-12"
    nota_fiscal_exemplo = "15095"
    resultado = await rastrear_accert(cnpj_exemplo, nota_fiscal_exemplo)

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    if resultado['status'] == 'sucesso':
        print(resultado['dados'])
    else:
        print(f"Falha no rastreamento: {resultado['erro']}")
    print("---------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
