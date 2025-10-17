from ..configs.logger_config import logger
from playwright.async_api import Error
from .base_scraper import BaseScraper
from ..configs.config import SCRAPER_URLS, TIMEOUTS
from .scrapper_data_model import ScraperResponse
from . import braspress_handler


class BrasspressScraper(BaseScraper):
    """Scraper for BRASPRESS logistics tracking."""

    def __init__(self):
        super().__init__("braspress")

    async def scrape(self, cnpj: str, nota_fiscal: str) -> ScraperResponse:
        """
        Realiza o web scraping do status de uma entrega no site da BRASPRESS.

        Args:
            cnpj: O CNPJ do remetente para a busca.
            nota_fiscal: O número da nota fiscal para a busca.

        Returns:
            ScraperResponse com as informações extraídas ou uma mensagem de erro.
        """
        page = await self.create_page()
        log_prefix = self._get_log_prefix(cnpj=cnpj, nota_fiscal=nota_fiscal)

        logger.info(f"{log_prefix} - Acessando a página de rastreamento da BRASPRESS")
        try:
            await page.goto(SCRAPER_URLS["braspress"], timeout=TIMEOUTS["page_load"])
        except Error as e:
            logger.error(f"{log_prefix} - Erro ao acessar a página: {e}")
            return self.error_response(
                "network_error", f"Erro ao acessar a página: {e}"
            )

        logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
        await page.fill("#cnpj-tracking", cnpj)

        logger.info(f"{log_prefix} - Preenchendo Nota Fiscal: {nota_fiscal}")
        nota_fiscal_input = await page.wait_for_selector(
            "#pedido-tracking", timeout=TIMEOUTS["selector_wait"]
        )
        await nota_fiscal_input.fill(nota_fiscal)

        logger.info(f"{log_prefix} - Fechando pop-up")
        await page.locator(f'svg:has(path[d*="{"M1490 1322q0 40"}"])').click()

        logger.info(f"{log_prefix} - Clicando no botão de busca")
        await page.locator(".search-tracking").click()

        logger.info(f"{log_prefix} - Aguardando a página de resultados carregar")
        await page.wait_for_load_state("networkidle")

        logger.info(f"{log_prefix} - Entrando no iframe de rastreamento")
        frame_locator = page.frame_locator("#iframe-tracking")

        logger.info(f"{log_prefix} - Clicando no botão detalhes de rastreamento")
        await frame_locator.get_by_text("Detalhes do Rastreamento").first.click()

        logger.info(f"{log_prefix} - Clicando no botão mais detalhes")
        await frame_locator.get_by_text("Mais Detalhes").first.click()

        logger.info(f"{log_prefix} - Extraindo informações da entrega")
        movimentacoes = await braspress_handler.parse_detailed_history(frame_locator)
        resumo_entrega = await braspress_handler.parse_summary_steps(frame_locator)
        data = {"resumo_etapas": resumo_entrega, "historico_detalhado": movimentacoes}

        logger.info(f"{log_prefix} - Dados extraídos: {data}")
        return self.success_response(data)
