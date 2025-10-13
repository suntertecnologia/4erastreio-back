import asyncio
from ..config.logger_config import logger
from playwright.async_api import async_playwright, TimeoutError

def treat_lista_ocorrencias(ocorrencias_raw: str) -> list:
    """
    Função para tratar a string de ocorrências retornada pelo scraper da Braspress.
    Esta função pode ser expandida conforme necessário para ajustar o formato
    dos dados ou extrair informações adicionais.

    Args:
        ocorrencias_raw: String bruta com as ocorrências do scraper.

    Returns:
        Lista de dicionários com as ocorrências tratadas.
    """
    ocorrencias = []
    for linha in ocorrencias_raw.split('\n'):
        linha = linha.strip()
        if linha:
            ocorrencias.append({
                "timestamp": None,  # Data/hora não disponível por evento na fonte
                "status": linha,
                "local": {
                    "cidade": None, # Não disponível por evento
                    "estado": None  # Não disponível por evento
                },
                "detalhes": "" # Não disponível
            })
    return ocorrencias

async def rastrear_viaverde(login: str, senha: str, n_rastreio: str) -> dict:
    """
    Realiza o web scraping do status de uma entrega no site da Via Verde.

    Args:
        cnpj: O CNPJ do remetente para a busca.
        login: O login para acessar o sistema.
        senha: A senha para acessar o sistema.
        nota_fiscal: O número da nota fiscal para a busca.

    Returns:
        Um dicionário com as informações extraídas ou uma mensagem de erro.
    """

    dados_entrega = {
        "status": "falha",
        "detalhes": ""
    }
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Mude para False para ver o navegador abrindo
        page = await browser.new_page()
        log_prefix = f"[NF: {n_rastreio}]" # Prefixo para identificar a entrega no logs
        try:
            logger.info(f"{log_prefix} - 1. Acessando a página de rastreamento da Via Verde")
            await page.goto("http://viaverde.supplytrack.com.br/login?ReturnUrl=%2f", timeout=60000)

        # --- LOGIN ---------
            logger.info(f"{log_prefix} - 2. Preenchendo login: {login}...")
            await page.fill("#login", login)

            logger.info(f"{log_prefix} - 3. Preenchendo senha: {senha}...")
            await page.fill("#senha", senha)

            logger.info(f"{log_prefix} - 4. Clicando no botão de busca...")
            await page.click('button:has-text("Entrar")')

            logger.info(f"{log_prefix} - 5. Clicando no botão de Consultas")
            await page.locator('a:has(i.fa-search)').click()

            logger.info(f"{log_prefix} - 6. Clicando no botão Por Documento")
            await page.get_by_text("Por Documento").click()

            logger.info(f"{log_prefix} - 7. Inserindo o n° rastreio: {n_rastreio}")
            await page.locator('#nrNf').fill(n_rastreio)

            logger.info(f"{log_prefix} - 8. Pesquisando status da entrega")
            await page.click('button:has-text("Pesquisar")')

            logger.info(f"{log_prefix} - 9. Coletando dados da tabela")
            primeira_linha = page.locator("table.dataTable tbody tr").first
            lista_de_ocorrencias = (await primeira_linha.locator("td.coluna-ocorrencias").text_content() or "").strip()
            dados_entrega = (await primeira_linha.locator("td.coluna-dtentrega").text_content() or "").strip()
            remetente = (await primeira_linha.locator("td.coluna-remetente").text_content() or "").strip()
            destinatario = (await primeira_linha.locator("td.coluna-destinatario").text_content() or "").strip()
            n_notafiscal = (await primeira_linha.locator("td.coluna-nrnf").text_content() or "").strip()

            dados_da_linha = {
                "data_entrega": dados_entrega,
                "remetente": remetente,
                "destinatario": destinatario,
                "n_rastreio": n_rastreio,
                "ocorrencias": treat_lista_ocorrencias(lista_de_ocorrencias),
                "n_notafiscal": n_notafiscal
            }

            resultado_final = {
                "status": "sucesso",
                "dados": dados_da_linha  # ATENÇÃO: 'dados' agora é um único objeto, não uma lista
            }

        except TimeoutError:
            print("\nERRO: O tempo para encontrar um elemento expirou. Verifique os seletores ou a velocidade da sua conexão.")
            dados_entrega["detalhes"] = "Erro de timeout. O site demorou muito para responder ou a estrutura da página mudou."
        except Exception as e:
            logger.exception(f"{log_prefix} - Ocorreu um erro inesperado: {e}")
            await page.screenshot(path='erro_accert.png') # Tira uma foto da tela para ajudar a depurar
            dados_entrega["detalhes"] = {"error": str(e)}

        finally:
            await browser.close()
            logger.info(f"{log_prefix} - 10. Navegador fechado.")

    return resultado_final