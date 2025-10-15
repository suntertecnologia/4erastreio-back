# from fastapi.testclient import TestClient
# from app import app

# client = TestClient(app)

# def test_read_root():
#     """
#     Testa o endpoint raiz (/) da API.
#     """
#     # Act
#     response = client.get("/")

#     # Assert
#     assert response.status_code == 200
#     assert response.json() == {"message": "Welcome to the SunterCode Tracking API"}

# def test_receber_json_success():
#     """
#     Testa o endpoint /receber_json com um payload válido.
#     """
#     # Arrange: Cria um payload de exemplo válido
#     test_payload = {
#         "informacoes_gerais": {
#             "transportadora": "teste",
#             "codigo_rastreio": "12345",
#             "numero_nf": "67890",
#             "previsao_entrega": "2025-10-14",
#             "data_postagem": "2025-10-10",
#             "remetente": {"nome": "Empresa Remetente", "cnpj": "11.111.111/0001-11"},
#             "destinatario": {"nome": "Empresa Destinatário", "cnpj": "22.222.222/0001-22"}
#         },
#         "historico": [
#             {
#                 "timestamp": "2025-10-10T10:00:00",
#                 "status": "postado",
#                 "local": {"cidade": "Origem", "estado": "SP"},
#                 "detalhes": "Objeto postado"
#             }
#         ],
#         "erro": None
#     }

#     # Act: Envia a requisição para a API
#     response = client.post("/receber_json", json=test_payload)

#     # Assert: Verifica a resposta
#     assert response.status_code == 200
#     response_data = response.json()
#     assert response_data["status"] == "sucesso"
#     assert response_data["dados_recebidos"] == test_payload
