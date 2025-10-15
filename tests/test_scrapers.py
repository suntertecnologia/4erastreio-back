# import pytest
# from src.scrapers.braspress_scraper import rastrear_braspress
# from src.scrapers.accert_scraper import rastrear_accert
# from src.scrapers.viaverde_scraper import rastrear_viaverde
# from src.scrapers.jamef_scraper import rastrear_jamef
# from src.scrapers.scrapper_data_model import ScraperResponse


# def assert_output_scraper(response):
#     """
#     Testa o formato do output do scraper
#     """
#     # Assert: Verifica a estrutura e o conteúdo da resposta
#     assert response is not None
#     assert response["status"] == "sucesso"
#     assert response["erro"] is None

#     dados = response.get("dados")
#     assert dados is not None

#     # Verifica se a estrutura dos dados corresponde a StandardizedDeliveryData
#     assert "informacoes_gerais" in dados
#     assert "historico" in dados

#     historico = dados["historico"]
#     assert isinstance(historico, list)
#     # Verifica se há pelo menos um evento no histórico (pode variar)
#     if len(historico) > 0:
#         evento = historico[0]
#         assert "timestamp" in evento
#         assert "status" in evento
#         assert "local" in evento
#         assert "detalhes" in evento


# @pytest.mark.asyncio
# async def test_rastrear_braspress():
#     """
#     Testa o rastreamento da Braspress com um CNPJ e nota fiscal válidos.
#     Este é um teste de integração, pois depende do serviço externo da Braspress.
#     """
#     cnpj = "34.122.358/0001-09"  # CNPJ de exemplo
#     nota_fiscal = "8231"  # Nota fiscal de exemplo

#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await rastrear_braspress(cnpj, nota_fiscal)

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
#     response: ScraperResponse = await rastrear_accert(cnpj, nota_fiscal)

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

#     # Act: Chama a função de rastreamento
#     response: ScraperResponse = await rastrear_viaverde(
#         login, senha, n_rastreio="118895"
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
#     response: ScraperResponse = await rastrear_jamef(cnpj, nota_fiscal)

#     # Assert estrutura do scraper
#     assert_output_scraper(response)
