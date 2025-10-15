import regex as re
from ..configs.logger_config import logger
from .base_scraper import BaseScraper
from ..configs.config import SCRAPER_URLS, TIMEOUTS
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
        await page.get_by_placeholder("insira o n° da nota fiscal").fill(
            re.sub("[^0-9]", "", nota_fiscal)
        )

        # 3. Clicar no primeiro botão de pesquisa
        logger.info(f"{log_prefix} - Clicando no botão de busca")
        await page.click('button:has-text("PESQUISAR")')

        # 4. Preencher CNPJ
        logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
        await page.get_by_placeholder("insira o CPF / CNPJ").fill(
            re.sub("[^0-9]", "", cnpj)
        )

        # 5. Clicar no segundo botão de pesquisa
        logger.info(f"{log_prefix} - Clicando no botão de busca novamente")
        await page.click('button:has-text("PESQUISAR")')

        # 6. Aguardar página de resultados carregar
        logger.info(f"{log_prefix} - Aguardando a página de resultados carregar")
        await page.wait_for_load_state("networkidle")

        # 7. Clicar no botão de histórico
        logger.info(f"{log_prefix} - Clicando no botão de histórico")
        async with page.expect_response(
            "https://px.ads.linkedin.com/wa/?medium=fetch&fmt=g"
        ):
            await page.click('button:has-text("Histórico")')

        # 8. Extrair informações da entrega
        logger.info(f"{log_prefix} - Extraindo informações da entrega")
        seletor_container = ".content"
        await page.wait_for_selector(
            seletor_container, timeout=TIMEOUTS["selector_wait"]
        )
        detalhes_texto = await page.inner_text(seletor_container)

        # Retornar dados estruturados
        dados = {"detalhes": detalhes_texto.strip()}
        logger.info(f"{log_prefix} - Dados extraídos: {dados}")
        return self.success_response(dados)
