import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from src.configs.config import (
    BASE_URL,
    ORCHESTRATOR_USER_EMAIL,
    ORCHESTRATOR_USER_PASSWORD,
)


def create_user():
    url = f"{BASE_URL}/auth/register"
    user_data = {
        "email": ORCHESTRATOR_USER_EMAIL,
        "password": ORCHESTRATOR_USER_PASSWORD,
    }
    response = requests.post(url, json=user_data)
    if response.status_code == 200:
        print("Orchestrator user created successfully.")
    else:
        print(f"Error creating orchestrator user: {response.text}")


if __name__ == "__main__":
    create_user()
