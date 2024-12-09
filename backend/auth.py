import json
from spotipy.oauth2 import SpotifyOAuth  # type: ignore
import os

with open("config.json", "r") as config_file:
    config = json.load(config_file)

SPOTIPY_CLIENT_ID = config["SPOTIFY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = config["SPOTIFY_CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = config["SPOTIFY_REDIRECT_URI"]

# Updated scopes to include 'streaming'
SCOPES = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-read-private "
    "streaming"
)

def get_spotify_auth():
    """Returns a SpotifyOAuth object for handling authentication."""
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPES,
    )

def get_auth_url():
    """Generate and return the Spotify login URL."""
    sp_oauth = get_spotify_auth()
    return sp_oauth.get_authorize_url()

def get_tokens(auth_code):
    sp_oauth = get_spotify_auth()
    token_info = sp_oauth.get_access_token(auth_code)
    print("Token Scopes:", token_info["scope"])
    return token_info

def refresh_token(refresh_token):
    """Refresh access token using Spotipy."""
    sp_oauth = get_spotify_auth()
    return sp_oauth.refresh_access_token(refresh_token)
