# import pytest
# from src.scrapers.runner import run_scraper as runner
# from src.scrapers.scrapper_data_model import ScraperResponse


# def assert_output_scraper(response):
#     """
#     Testa o formato do output do scraper
#     """
#     # Assert: Verifica a estrutura e o conteúdo da resposta
#     assert response is not None
#     assert response["erro"] is None
#     print(response)


# @pytest.mark.asyncio
# async def test_rastrear_braspress():
#     """
#     Testa o rastreamento da Braspress com um CNPJ e nota fiscal válidos.
#     Este é um teste de integração, pois depende do serviço externo da Braspress.
#     """
#     cnpj = "34.122.358/0001-09"  # CNPJ de exemplo
#     nota_fiscal = "8231"  # Nota fiscal de exemplo

#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await runner("braspress", nota_fiscal, cnpj)

#     # Assert estrutura do scraper
#     assert_output_scraper(response)


# @pytest.mark.asyncio
# async def test_rastrear_accert_success():
#     """
#     Testa o rastreamento da Braspress com um CNPJ e nota fiscal válidos.
#     Este é um teste de integração, pois depende do serviço externo da Braspress.
#     """
#     cnpj = "11.173.954/0001-12"  # CNPJ de exemplo
#     nota_fiscal = "15095"  # Nota fiscal de exemplo

#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await runner("accert", nota_fiscal, cnpj)

#     # Assert estrutura do scraper
#     assert_output_scraper(response)


# @pytest.mark.asyncio
# async def test_rastrear_viaverde_success():
#     """
#     Testa o rastreamento da Braspress com um CNPJ e nota fiscal válidos.
#     Este é um teste de integração, pois depende do serviço externo da Braspress.
#     """
#     login = "pedidos.quatroestacoes"  # CNPJ de exemplo
#     senha = "4Edecoracoes"  # Nota fiscal de exemplo
#     nota_fiscal = 117024
#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await runner(
#         "viaverde",
#         nota_fiscal,
#         "343",
#         credentials={"username": login, "password": senha},
#     )

#     # Assert estrutura do scraper
#     assert_output_scraper(response)


# @pytest.mark.asyncio
# async def test_rastrear_jamef_success():
#     """
#     Testa o rastreamento da Braspress com um CNPJ e nota fiscal válidos.
#     Este é um teste de integração, pois depende do serviço externo da Braspress.
#     """
#     cnpj = "48.775.1910001-90"  # CNPJ de exemplo
#     nota_fiscal = "1160274"  # Nota fiscal de exemplo

#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await runner("jamef", nota_fiscal, cnpj)

#     # Assert estrutura do scraper
#     assert_output_scraper(response)
