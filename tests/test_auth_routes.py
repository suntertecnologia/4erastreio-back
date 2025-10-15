# from fastapi.testclient import TestClient


# def test_register(client: TestClient):
#     response = client.post(
#         "/auth/register",
#         json={"email": "test@example.com", "password": "testpassword"},
#     )
#     assert response.status_code == 200
#     assert response.json()["email"] == "test@example.com"


# def test_login(client: TestClient):
#     client.post(
#         "/auth/register",
#         json={"email": "test2@example.com", "password": "testpassword"},
#     )
#     response = client.post(
#         "/auth/login",
#         json={"email": "test2@example.com", "password": "testpassword"},
#     )
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert "refresh_token" in response.json()
