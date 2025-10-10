import asyncio
from ..config.logger_config import logger
from playwright.async_api import async_playwright, TimeoutError

async def rastrear_viaverde(login: str, senha: str, nota_fiscal: str) -> dict:
    """
    Realiza o web scraping do status de uma entrega no site da Via Verde.

    Args:
        cnpj: O CNPJ do remetente para a busca.
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
        log_prefix = f"[NF: {nota_fiscal}]" # Prefixo para identificar a entrega no logs
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

        except TimeoutError:
            print("\nERRO: O tempo para encontrar um elemento expirou. Verifique os seletores ou a velocidade da sua conexão.")
            dados_entrega["detalhes"] = "Erro de timeout. O site demorou muito para responder ou a estrutura da página mudou."
        except Exception as e:
            logger.exception(f"{log_prefix} - Ocorreu um erro inesperado: {e}")
            await page.screenshot(path='erro_accert.png') # Tira uma foto da tela para ajudar a depurar
            dados_entrega["detalhes"] = {"error": str(e)}

        finally:
            await browser.close()
            logger.info(f"{log_prefix} - 7. Navegador fechado.")

    return dados_entrega

async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com uma Nota Fiscal para testar
    nota_fiscal_exemplo = "15095"
    login_exemplo = "pedidos@quatroestacoesdecoracoes.com.br"
    senha_exemplo = "4estacoes"
    resultado = await rastrear_viaverde(login_exemplo, senha_exemplo, nota_fiscal_exemplo)

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    if resultado['status'] == 'sucesso':
        print(resultado['detalhes'])
    else:
        print(f"Falha no rastreamento: {resultado['detalhes']}")
    print("---------------------------------")


if __name__ == "__main__":
    asyncio.run(main())