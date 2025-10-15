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


# def test_auth_register():
#     """
#     Testa o endpoint /receber_json com um payload válido.
#     """
#     # Create mock user
#     email = "teste@testinho.com"
#     password = "123"
#     test_payload = {"email": email, "password": password}
#     # Act: Envia a requisição para a API
#     response = client.post("/auth/register", json=test_payload)

#     # Assert: Verifica a resposta
#     assert response.status_code == 200
#     response_data = response.json()
#     assert response_data == {
#         "nome": "teste",
#         "email": email,
#         "cargo": "user",
#         "is_active": True,
#     }
