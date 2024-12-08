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

def start_playback(song_uri=None):
    """Start playback on the user's Spotify account."""
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        raise Exception("Access token not found. Please log in.")

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.spotify.com/v1/me/player/play"

    if song_uri:
        payload = {"uris": [song_uri]}
    else:
        payload = {}  # Resume playback

    response = requests.put(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json() if response.content else {}

def pause_playback():
    """Pause playback on the user's Spotify account."""
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        raise Exception("Access token not found. Please log in.")

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.spotify.com/v1/me/player/pause"

    try:
        response = requests.put(url, headers=headers)
        if response.status_code == 204:
            return {"message": "Playback paused successfully"}
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print("403 Error: Player command failed. Defaulting to success for now.")
            return {"message": "Playback paused (defaulted for 403)."}
        else:
            raise e
def validate_access_token():
    """Check if the access token is valid."""
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        return False

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.spotify.com/v1/me"  # Endpoint to fetch user profile

    response = requests.get(url, headers=headers)
    if response.status_code == 401:  # Unauthorized
        return False
    response.raise_for_status()
    return True

def stop_playback():
    """Stop playback (not directly supported by Spotify; pause instead)."""
    return pause_playback()