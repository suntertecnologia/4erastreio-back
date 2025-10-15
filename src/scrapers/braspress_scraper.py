import re
from ..configs.logger_config import logger
from playwright.async_api import Page
from .base_scraper import BaseScraper
from ..configs.config import SCRAPER_URLS, TIMEOUTS
from .scrapper_data_model import ScraperResponse


async def _parse_detailed_history(page: Page) -> list[dict]:
    """Função auxiliar para extrair o histórico detalhado da timeline vertical."""
    history_events = []
    container = page.locator("#timeline2482705908231")

    # Encontra todas as entradas individuais na timeline
    event_locators = await container.locator(
        ".vertical-time-line._tracking-datail"
    ).all()

    for event_locator in event_locators:
        status_text = ""
        timestamp_text = ""

        # Pega a descrição do status
        info_loc = event_locator.locator(".vertical-time-line-info")
        if await info_loc.count() > 0:
            status_text = await info_loc.inner_text()
            # Limpa o texto, removendo tags <br> e outros elementos internos
            status_text = re.sub(r"<br>.*", "", status_text).strip()

        # Pega a data e hora
        date_loc = event_locator.locator(".vertical-time-line-date")
        if await date_loc.count() > 0:
            timestamp_text = (await date_loc.text_content() or "").strip()

        if status_text and timestamp_text:
            history_events.append({"timestamp": timestamp_text, "status": status_text})

    return history_events


async def _parse_summary_steps(page: Page) -> list[dict]:
    """Função auxiliar para extrair as etapas principais do resumo horizontal."""
    summary_steps = []
    container = page.locator("#row-step-tracking")

    # Encontra todas as etapas principais no "wizard"
    step_locators = await container.locator(".step-iten").all()

    for step_locator in step_locators:
        step_text = ""
        date_text = ""

        # Pega a descrição da etapa
        step_loc = step_locator.locator(".step-txt-up")
        if await step_loc.count() > 0:
            step_text = (await step_loc.text_content() or "").strip()

        # Pega a data da etapa
        date_loc = step_locator.locator(".step-txt-date")
        if await date_loc.count() > 0:
            date_text = (await date_loc.text_content() or "").strip()

        if step_text and date_text:
            summary_steps.append({"date": date_text, "step": step_text})

    return summary_steps


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

        # 1. Acessar página de rastreamento
        logger.info(f"{log_prefix} - Acessando a página de rastreamento da BRASPRESS")
        await page.goto(SCRAPER_URLS["braspress"], timeout=TIMEOUTS["page_load"])

        # 2. Preencher CNPJ
        logger.info(f"{log_prefix} - Preenchendo CNPJ: {cnpj}")
        await page.fill("#cnpj-tracking", cnpj)

        # 3. Preencher Nota Fiscal
        logger.info(f"{log_prefix} - Preenchendo Nota Fiscal: {nota_fiscal}")
        nota_fiscal_input = await page.wait_for_selector(
            "#pedido-tracking", timeout=TIMEOUTS["selector_wait"]
        )
        await nota_fiscal_input.fill(nota_fiscal)

        # 4. Fechar pop-up
        logger.info(f"{log_prefix} - Fechando pop-up")
        await page.locator(f'svg:has(path[d*="{"M1490 1322q0 40"}"])').click()

        # 5. Clicar no botão de busca
        logger.info(f"{log_prefix} - Clicando no botão de busca")
        await page.locator(".search-tracking").click()

        # 6. Aguardar página de resultados carregar
        logger.info(f"{log_prefix} - Aguardando a página de resultados carregar")
        await page.wait_for_load_state("networkidle")

        # 7. Entrar no iframe de rastreamento
        logger.info(f"{log_prefix} - Entrando no iframe de rastreamento")
        frame_locator = page.frame_locator("#iframe-tracking")

        # 8. Clicar no botão detalhes de rastreamento
        logger.info(f"{log_prefix} - Clicando no botão detalhes de rastreamento")
        await frame_locator.get_by_text("Detalhes do Rastreamento").first.click()

        # 9. Clicar no botão mais detalhes
        logger.info(f"{log_prefix} - Clicando no botão mais detalhes")
        await frame_locator.get_by_text("Mais Detalhes").first.click()

        # 10. Extrair informações da entrega
        logger.info(f"{log_prefix} - Extraindo informações da entrega")
        detailed_history = await _parse_detailed_history(frame_locator)
        summary_steps = await _parse_summary_steps(frame_locator)

        # Retornar dados estruturados
        dados = {
            "resumo_etapas": summary_steps,
            "historico_detalhado": detailed_history,
        }

        logger.info(f"{log_prefix} - Dados extraídos: {dados}")
        return self.success_response(dados)
