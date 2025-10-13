import asyncio
import regex as re
from ..config.logger_config import logger
from .base_scraper import BaseScraper
from .config import SCRAPER_URLS, TIMEOUTS
from .scrapper_data_model import ScraperResponse


class JamefScraper(BaseScraper):
    """Scraper for JAMEF logistics tracking."""

    def __init__(self):
        super().__init__("jamef")

    async def scrape(self, cnpj: str, nota_fiscal: str) -> ScraperResponse:
        """
        Realiza o web scraping do status de uma entrega no site da JAMEF.

        Args:
            cnpj: O CNPJ do remetente para a busca.
            nota_fiscal: O número da nota fiscal para a busca.

        Returns:
            ScraperResponse com as informações extraídas ou uma mensagem de erro.
        """
        page = await self.create_page()
        log_prefix = self._get_log_prefix(cnpj=cnpj, nota_fiscal=nota_fiscal)

        # 1. Acessar página de rastreamento
        logger.info(f"{log_prefix} - Acessando a página de rastreamento da JAMEF")
        await page.goto(SCRAPER_URLS["jamef"], timeout=TIMEOUTS["page_load"])

        # 2. Preencher número de pedido (nota fiscal)
        logger.info(f"{log_prefix} - Preenchendo número de pedido: {nota_fiscal}")
        await page.get_by_placeholder("insira o n° da nota fiscal").fill(re.sub('[^0-9]', '', nota_fiscal))

        # 3. Clicar no primeiro botão de pesquisa
        logger.info(f"{log_prefix} - Clicando no botão de busca")
        await page.click('button:has-text("PESQUISAR")')

        # 4. Preencher CNPJ
        logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
        await page.get_by_placeholder("insira o CPF / CNPJ").fill(re.sub('[^0-9]', '', cnpj))

        # 5. Clicar no segundo botão de pesquisa
        logger.info(f"{log_prefix} - Clicando no botão de busca novamente")
        await page.click('button:has-text("PESQUISAR")')

        # 6. Aguardar página de resultados carregar
        logger.info(f"{log_prefix} - Aguardando a página de resultados carregar")
        await page.wait_for_load_state("networkidle")

        # 7. Clicar no botão de histórico
        logger.info(f"{log_prefix} - Clicando no botão de histórico")
        async with page.expect_response("https://px.ads.linkedin.com/wa/?medium=fetch&fmt=g"):
            await page.click('button:has-text("Histórico")')

        # 8. Extrair informações da entrega
        logger.info(f"{log_prefix} - Extraindo informações da entrega")
        seletor_container = ".content"
        await page.wait_for_selector(seletor_container, timeout=TIMEOUTS["selector_wait"])
        detalhes_texto = await page.inner_text(seletor_container)

        # Retornar dados estruturados
        dados = {
            "detalhes": detalhes_texto.strip()
        }

        return self.success_response(dados)


async def rastrear_jamef(cnpj: str, nota_fiscal: str) -> dict:
    """
    Função wrapper para manter compatibilidade com código existente.

    Args:
        cnpj: O CNPJ do remetente para a busca.
        nota_fiscal: O número da nota fiscal para a busca.

    Returns:
        Um dicionário com as informações extraídas ou uma mensagem de erro.
    """
    scraper = JamefScraper()
    return await scraper.execute(cnpj=cnpj, nota_fiscal=nota_fiscal)


async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com um CNPJ e Nota Fiscal reais para testar
    cnpj_exemplo = "48.775.1910001-90"
    nota_fiscal_exemplo = "1160274"
    resultado = await rastrear_jamef(cnpj_exemplo, nota_fiscal_exemplo)

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    if resultado['status'] == 'sucesso':
        print(resultado['dados'])
    else:
        print(f"Falha no rastreamento: {resultado['erro']}")
    print("---------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
