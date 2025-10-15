# from fastapi.testclient import TestClient


# def test_create_entrega(client: TestClient):
#     # First, need to be authenticated
#     client.post(
#         "/auth/register",
#         json={"email": "entrega@example.com", "password": "testpassword"},
#     )
#     login_response = client.post(
#         "/auth/login",
#         json={"email": "entrega@example.com", "password": "testpassword"},
#     )
#     token = login_response.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     response = client.post(
#         "/entrega/",
#         headers=headers,
#         json={
#             "transportadora": "accert",
#             "codigo_rastreio": "12345",
#             "numero_nf": "67890",
#             "cliente": "Test Client",
#             "cnpj_destinatario": "11.111.111/0001-11",
#             "status": "Em andamento",
#         },
#     )
#     assert response.status_code == 201
#     assert response.json()["transportadora"] == "accert"


# def test_get_entrega(client: TestClient):
#     # First, need to be authenticated
#     client.post(
#         "/auth/register",
#         json={"email": "entrega2@example.com", "password": "testpassword"},
#     )
#     login_response = client.post(
#         "/auth/login",
#         json={"email": "entrega2@example.com", "password": "testpassword"},
#     )
#     token = login_response.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     create_response = client.post(
#         "/entrega/",
#         headers=headers,
#         json={
#             "transportadora": "accert",
#             "codigo_rastreio": "54321",
#             "numero_nf": "98765",
#             "cliente": "Test Client 2",
#             "cnpj_destinatario": "22.222.222/0001-22",
#             "status": "Em andamento",
#         },
#     )
#     entrega_id = create_response.json()["id"]

#     response = client.get(f"/entrega/{entrega_id}", headers=headers)
#     assert response.status_code == 200
#     assert response.json()["id"] == entrega_id
