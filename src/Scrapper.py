import asyncio
from playwright.async_api import async_playwright, TimeoutError
import time

async def rastrear_accert(cnpj: str, nota_fiscal: str) -> dict:
    """
    Realiza o web scraping do status de uma entrega no site da ACCERT.

    Args:
        cnpj: O CNPJ do remetente para a busca.
        nota_fiscal: O número da nota fiscal para a busca.

    Returns:
        Um dicionário com as informações extraídas ou uma mensagem de erro.
    """
    dados_entrega = {"status": "erro", "detalhes": "Não foi possível rastrear a encomenda."}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Mude para False para ver o navegador abrindo
        page = await browser.new_page()

        try:
            print("1. Acessando a página de rastreamento da ACCERT...")
            await page.goto("https://cliente.accertlogistica.com.br/rastreamento", timeout=60000)

            # --- PREENCHIMENTO DOS DADOS ---
            print(f"2. Preenchendo CNPJ: {cnpj}...")
            await page.fill("#cnpjOrCpf", cnpj)

            print(f"3. Preenchendo Nota Fiscal: {nota_fiscal}...")
            nota_fiscal_input = await page.wait_for_selector('#notaFiscal')
            await nota_fiscal_input.fill(nota_fiscal)

            print("4. Clicando no botão de busca...")
            await page.click('button:has-text("Buscar encomendas")')
            
            # --- AGUARDAR E EXPANDIR DETALHES ---
            print("5. Aguardando resultados e clicando para ver detalhes...")
            await page.get_by_role('button', name='Ver detalhes').click()
            
            # --- EXTRAÇÃO DAS INFORMAÇÕES ---
            print("6. Extraindo informações da entrega...")
            seletor_container = ".border-separation"
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
            print(f"\nOcorreu um erro inesperado: {e}")
            await page.screenshot(path='erro_accert.png') # Tira uma foto da tela para ajudar a depurar
            print("Uma captura de tela 'erro_accert.png' foi salva para análise.")
            dados_entrega["detalhes"] = f"Erro inesperado: {e}"

        finally:
            await browser.close()
            print("7. Navegador fechado.")

    return dados_entrega


async def main():
    # --- DADOS DE EXEMPLO ---
    # Substitua com um CNPJ e Nota Fiscal reais para testar
    cnpj_exemplo = "11.173.954/0001-12"
    nota_fiscal_exemplo = "15095"
    time_start =  time.time()
    resultado = await rastrear_accert(cnpj_exemplo, nota_fiscal_exemplo)
    time_end = time.time()
   

    print("\n--- RESULTADO DO RASTREAMENTO ---")
    if resultado['status'] == 'sucesso':
        print(resultado['detalhes'])
    else:
        print(f"Falha no rastreamento: {resultado['detalhes']}")
    print("---------------------------------")
    print(f"Tempo total de execução: {time_end - time_start:.2f} segundos")


if __name__ == "__main__":
    asyncio.run(main())