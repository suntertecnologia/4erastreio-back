import asyncio
from ..config.logger_config import logger
from playwright.async_api import async_playwright, TimeoutError, Page, Locator
import json
import re

async def _parse_detailed_history(page: Page) -> list[dict]:
    """Função auxiliar para extrair o histórico detalhado da timeline vertical."""
    history_events = []
    container = page.locator("#timeline2482705908231")  # Ajuste o ID conforme necessário
    
    # Encontra todas as entradas individuais na timeline
    event_locators = await container.locator(".vertical-time-line._tracking-datail").all()
    
    for event_locator in event_locators:
        status_text = ""
        timestamp_text = ""
        
        # Pega a descrição do status
        info_loc = event_locator.locator(".vertical-time-line-info")
        if await info_loc.count() > 0:
            status_text = await info_loc.inner_text()
            # Limpa o texto, removendo tags <br> e outros elementos internos
            status_text = re.sub(r'<br>.*', '', status_text).strip()

        # Pega a data e hora
        date_loc = event_locator.locator(".vertical-time-line-date")
        if await date_loc.count() > 0:
            timestamp_text = (await date_loc.text_content() or "").strip()
            
        if status_text and timestamp_text:
            history_events.append({
                "timestamp": timestamp_text,
                "status": status_text
            })
            
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
            summary_steps.append({
                "date": date_text,
                "step": step_text
            })
            
    return summary_steps

async def rastrear_braspress(cnpj: str, nota_fiscal: str) -> dict:
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
            await page.goto("https://www.braspress.com/", timeout=60000)

            # --- PREENCHIMENTO DOS DADOS ---
            logger.info(f"{log_prefix} - 2. Preenchendo CNPJ: {cnpj}...")
            await page.fill("#cnpj-tracking", cnpj)

            logger.info(f"{log_prefix} - 3. Preenchendo Nota Fiscal: {nota_fiscal}...")
            nota_fiscal_input = await page.wait_for_selector('#pedido-tracking')
            await nota_fiscal_input.fill(nota_fiscal)

            logger.info(f"{log_prefix} - 4. Fechando pop-up")
            await page.locator(f'svg:has(path[d*="{"M1490 1322q0 40"}"])').click()
        
            logger.info(f"{log_prefix} - 5. Clicando no botão de busca...")
            await page.locator('.search-tracking').click()

            logger.info(f"{log_prefix} - 6. Aguardando a página de resultados carregar...")
            await page.wait_for_load_state("networkidle") # Espera a rede ficar ociosa

            logger.info(f"{log_prefix} - 7. Entrando o iframe de rastreamento...")
            frame_locator = page.frame_locator("#iframe-tracking")

            await page.wait_for_timeout(10000)

            logger.info(f"{log_prefix} - 8. Clicando no botão detalhes de rastreamento")
            await frame_locator.get_by_text("Detalhes do Rastreamento").click()

            logger.info(f"{log_prefix} - 9. Clicando no botão mais detalhes")
            await frame_locator.get_by_text("Mais Detalhes").click()    
            
            # --- EXTRAÇÃO DAS INFORMAÇÕES ---
            detailed_history = await _parse_detailed_history(frame_locator)
            summary_steps = await _parse_summary_steps(frame_locator)

            # Monta o resultado final
            dados_entrega = {
                "status": "sucesso",
                "dados": {
                "resumo_etapas": summary_steps,
                "historico_detalhado": detailed_history}
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
        return dados_entrega
    
async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com um CNPJ e Nota Fiscal reais para testar
    cnpj_exemplo = "34.122.358/0001-09"
    nota_fiscal_exemplo = "8231"
    # Supondo que sua função principal de scraper se chame rastrear_braspress
    resultado = await rastrear_braspress(cnpj_exemplo, nota_fiscal_exemplo)

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    
    # --- CORREÇÃO APLICADA AQUI ---
    # 1. Verificamos se o status é de sucesso
    if resultado and resultado.get('status') == 'sucesso':
        # 2. Acessamos a chave correta ('dados')
        # 3. Usamos json.dumps para formatar a saída de forma legível
        print(json.dumps(resultado['dados'], indent=2, ensure_ascii=False))
    else:
        # Se deu erro, imprime o dicionário de resultado inteiro
        print(f"Ocorreu uma falha no rastreamento: {resultado}")

if __name__ == "__main__":
    asyncio.run(main())
