from ..configs.logger_config import logger
from .base_scraper import BaseScraper
from ..configs.config import SCRAPER_URLS
from .scrapper_data_model import ScraperResponse


def treat_lista_ocorrencias(ocorrencias_raw: str) -> list:
    """
    Função para tratar a string de ocorrências retornada pelo scraper.
    Esta função pode ser expandida conforme necessário para ajustar o formato
    dos dados ou extrair informações adicionais.

    Args:
        ocorrencias_raw: String bruta com as ocorrências do scraper.

    Returns:
        Lista de dicionários com as ocorrências tratadas.
    """
    ocorrencias = []
    for linha in ocorrencias_raw.split("\n"):
        linha = linha.strip()
        if linha:
            ocorrencias.append(
                {
                    "timestamp": None,
                    "status": linha,
                    "local": {"cidade": None, "estado": None},
                    "detalhes": "",
                }
            )
    return ocorrencias


class ViaVerdeScraper(BaseScraper):
    """Scraper for Via Verde logistics tracking."""

    def __init__(self):
        super().__init__("viaverde")

    async def scrape(self, login: str, senha: str, n_rastreio: str) -> ScraperResponse:
        """
        Realiza o web scraping do status de uma entrega no site da Via Verde.

        Args:
            login: O login para acessar o sistema.
            senha: A senha para acessar o sistema.
            n_rastreio: O número de rastreio para a busca.

        Returns:
            ScraperResponse com as informações extraídas ou uma mensagem de erro.
        """
        page = await self.create_page()
        log_prefix = self._get_log_prefix(n_rastreio=n_rastreio)

        # 1. Acessar página de rastreamento
        logger.info(f"{log_prefix} - Acessando a página de rastreamento da Via Verde")
        await page.goto(SCRAPER_URLS["viaverde"], timeout=60000)

        # 2. Fazer login - Preencher login
        logger.info(f"{log_prefix} - Preenchendo login: {login}")
        await page.fill("#login", login)

        # 3. Preencher senha
        logger.info(f"{log_prefix} - Preenchendo senha")
        await page.fill("#senha", senha)

        # 4. Clicar no botão de entrar
        logger.info(f"{log_prefix} - Clicando no botão de entrar")
        await page.click('button:has-text("Entrar")')

        # 5. Clicar no botão de Consultas
        logger.info(f"{log_prefix} - Clicando no botão de Consultas")
        await page.locator("a:has(i.fa-search)").click()

        # Wait for the "Por Documento" link to be visible
        por_documento_link = page.get_by_text("Por Documento")
        await por_documento_link.wait_for(state="visible", timeout=30000)

        # 6. Clicar no botão Por Documento
        logger.info(f"{log_prefix} - Clicando no botão Por Documento")
        await por_documento_link.click()

        # 7. Inserir número de rastreio
        logger.info(f"{log_prefix} - Inserindo o n° rastreio: {n_rastreio}")
        await page.locator("#nrNf").fill(n_rastreio)

        # 8. Pesquisar status da entrega
        logger.info(f"{log_prefix} - Pesquisando status da entrega")
        await page.click('button:has-text("Pesquisar")')

        # 9. Coletar dados da tabela
        logger.info(f"{log_prefix} - Coletando dados da tabela")
        primeira_linha = page.locator("table.dataTable tbody tr").first
        lista_de_ocorrencias = (
            await primeira_linha.locator("td.coluna-ocorrencias").text_content() or ""
        ).strip()
        data_entrega = (
            await primeira_linha.locator("td.coluna-dtentrega").text_content() or ""
        ).strip()
        remetente = (
            await primeira_linha.locator("td.coluna-remetente").text_content() or ""
        ).strip()
        destinatario = (
            await primeira_linha.locator("td.coluna-destinatario").text_content() or ""
        ).strip()
        n_notafiscal = (
            await primeira_linha.locator("td.coluna-nrnf").text_content() or ""
        ).strip()

        # Retornar dados estruturados
        dados = {
            "data_entrega": data_entrega,
            "remetente": remetente,
            "destinatario": destinatario,
            "n_rastreio": n_rastreio,
            "ocorrencias": treat_lista_ocorrencias(lista_de_ocorrencias),
            "n_notafiscal": n_notafiscal,
        }

        logger.info(f"{log_prefix} - Dados extraídos: {dados}")
        return self.success_response(dados)
