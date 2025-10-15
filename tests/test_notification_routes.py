# from fastapi.testclient import TestClient
# from unittest.mock import patch


# def test_send_notifications(client: TestClient):
#     # First, need to be authenticated
#     client.post(
#         "/auth/register",
#         json={"email": "shrekshrugers@gmail.com", "password": "testpassword"},
#     )
#     login_response = client.post(
#         "/auth/login",
#         json={"email": "shrekshrugers@gmail.com", "password": "testpassword"},
#     )
#     token = login_response.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}

#     with patch(
#         "src.notification.notification_handler.process_pending_notifications"
#     ) as mock_process:
#         response = client.post("/notification/send-notifications", headers=headers)
#         assert response.status_code == 202
#         assert response.json() == {
#             "message": "Notification process initiated in the background."
#         }
#         mock_process.assert_called_once()
