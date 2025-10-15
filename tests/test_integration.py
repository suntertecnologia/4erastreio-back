# import requests
# import time
# import logging
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from src.db.models import Usuario

# BASE_URL = "http://127.0.0.1:8000"
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# logger = logging.getLogger(__name__)


# def test_integration():
#     headers = {}
#     try:
#         # 1. Create a user
#         logger.info("Creating user...")
#         response = requests.post(
#             f"{BASE_URL}/auth/register",
#             json={"email": "shrekshrugers@gmail.com", "password": "testpassword"},
#         )
#         logger.info(f"Create user response: {response.status_code} {response.text}")
#         response.raise_for_status()

#         # 2. Login
#         logger.info("Logging in...")
#         login_response = requests.post(
#             f"{BASE_URL}/auth/login",
#             json={"email": "shrekshrugers@gmail.com", "password": "testpassword"},
#         )
#         logger.info(
#             f"Login response: {login_response.status_code} {login_response.text}"
#         )
#         login_response.raise_for_status()
#         token = login_response.json()["access_token"]
#         headers = {"Authorization": f"Bearer {token}"}

#         # 3. Create a delivery
#         logger.info("Creating delivery...")
#         create_response = requests.post(
#             f"{BASE_URL}/entrega/",
#             headers=headers,
#             json={
#                 "transportadora": "accert",
#                 "codigo_rastreio": "12345",
#                 "numero_nf": "67890",
#                 "cliente": "Shrek",
#                 "cnpj_destinatario": "11.111.111/0001-11",
#                 "status": "Em andamento",
#             },
#         )
#         logger.info(
#             f"Create delivery response: {create_response.status_code} {create_response.text}"
#         )
#         create_response.raise_for_status()

#         # 4. Trigger notification
#         logger.info("Triggering notification...")
#         response = requests.post(
#             f"{BASE_URL}/notification/send-notifications", headers=headers
#         )
#         logger.info(
#             f"Trigger notification response: {response.status_code} {response.text}"
#         )
#         response.raise_for_status()

#         # 5. Check log file for email success message
#         logger.info("Waiting for email to be sent...")
#         time.sleep(10)  # Increased wait time
#         logger.info("Checking log file...")

#     finally:
#         # 6. Cleanup
#         # logger.info(f"Cleaning up user {user_id}...")
#         db = TestingSessionLocal()
#         user = (
#             db.query(Usuario).filter(Usuario.email == "shrekshrugers@gmail.com").first()
#         )
#         if user:
#             db.delete(user)
#             db.commit()
#             db.close()
