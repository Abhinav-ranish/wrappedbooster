import requests
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(__file__).parent.parent / ".user"
load_dotenv(dotenv_path)

BACKEND_URL = "http://localhost:8000"

def get_login_url():
    """Fetch the login URL from the backend."""
    response = requests.get(f"{BACKEND_URL}/login")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")  # Log raw response for debugging
    response.raise_for_status()
    return response.json().get("auth_url")


def refresh_tokens():
    """Refresh tokens using the backend."""
    refresh_token = os.getenv("REFRESH_TOKEN")
    if not refresh_token:
        raise Exception("Refresh token not found in .user file.")

    response = requests.post(f"{BACKEND_URL}/refresh", json={"refresh_token": refresh_token})
    response.raise_for_status()
    return response.json()
