import asyncio
from ..config.logger_config import logger
from playwright.async_api import async_playwright, TimeoutError
import regex as re

async def rastrear_jamef(cnpj: str, nota_fiscal: str) -> dict:
    """
    Realiza o web scraping do status de uma entrega no site da BRASPRESS.

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
        log_prefix = f"[CNPJ: {cnpj}, NF: {nota_fiscal}]" # Prefixo para identificar a entrega no logs

        try:
            logger.info(f"{log_prefix} - 1. Acessando a página de rastreamento da BrassPRESS")
            await page.goto("https://www.jamef.com.br/", timeout=60000)

            # --- PREENCHIMENTO DOS DADOS ---
            logger.info(f"{log_prefix} - 2. Preenchendo número de pedido: {nota_fiscal}...")
            await page.get_by_placeholder("insira o n° da nota fiscal").fill(re.sub('[^0-9]', '', nota_fiscal))

            logger.info(f"{log_prefix} - 3. Clicando no botão de busca...")
            await page.click('button:has-text("PESQUISAR")')

            logger.info(f"{log_prefix} - 4. Preenchendo CNPJ: {cnpj}...")
            await page.get_by_placeholder("insira o CPF / CNPJ").fill((re.sub('[^0-9]', '', cnpj)))

            logger.info(f"{log_prefix} - 5. Clicando no botão de busca...")
            await page.click('button:has-text("PESQUISAR")')

            logger.info(f"{log_prefix} - 6. Aguardando a página de resultados carregar...")
            await page.wait_for_load_state("networkidle") # Espera a rede ficar ociosa

            logger.info(f"{log_prefix} - 7. Clicando no botão de histórico")
            async with page.expect_response("https://px.ads.linkedin.com/wa/?medium=fetch&fmt=g"): # <-- SUBSTITUA PELA URL QUE VOCÊ ENCONTROU
                await page.click('button:has-text("Histórico")')

            logger.info(f"{log_prefix} - 8. Extraindo informações da entrega...")
            seletor_container = ".content"
            await page.wait_for_selector(seletor_container, timeout=15000)
            detalhes_texto = await page.inner_text(seletor_container)

            dados_entrega = {
                "status": "sucesso",
                "detalhes": detalhes_texto.strip()
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
            logger.info(f"{log_prefix} - 9. Navegador fechado.")
        return dados_entrega
    
async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com um CNPJ e Nota Fiscal reais para testar
    cnpj_exemplo = "48.775.1910001-90"
    nota_fiscal_exemplo = "1160274"
    resultado = await rastrear_jamef(cnpj_exemplo, nota_fiscal_exemplo)

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    if resultado['status'] == 'sucesso':
        print(resultado['detalhes'])
    else:
        print(f"Falha no rastreamento: {resultado['detalhes']}")
    print("---------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
