import asyncio
from asyncio import Lock
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect # type: ignore
from fastapi.responses import RedirectResponse, HTMLResponse # type: ignore
from spotipy import Spotify, SpotifyException # type: ignore
from auth import get_auth_url, get_tokens, refresh_token
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles



dotenv_path = Path(__file__).parent.parent / ".user"  # Adjust for relative paths
load_dotenv(dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
EXPIRES_IN = os.getenv("EXPIRES_IN")
TOKEN_EXPIRY_TIME = None  # Tracks token expiry time

app = FastAPI()

def update_env(tokens):
    try:
        with open(dotenv_path, "w") as f:
            f.write(f"ACCESS_TOKEN={tokens['access_token']}\n")
            f.write(f"REFRESH_TOKEN={tokens['refresh_token']}\n")
            f.write(f"EXPIRES_IN={tokens['expires_in']}\n")
        global ACCESS_TOKEN, REFRESH_TOKEN
        ACCESS_TOKEN = tokens['access_token']
        REFRESH_TOKEN = tokens['refresh_token']
        set_token_expiry(tokens['expires_in'])
    except Exception as e:
        print(f"Error updating tokens: {e}")

def is_token_expired():
    if TOKEN_EXPIRY_TIME is None:
        return True
    return datetime.now() >= TOKEN_EXPIRY_TIME

def set_token_expiry(expires_in):
    global TOKEN_EXPIRY_TIME
    TOKEN_EXPIRY_TIME = datetime.now() + timedelta(seconds=int(expires_in))

def refresh_access_token_if_needed():
    global ACCESS_TOKEN, REFRESH_TOKEN
    if is_token_expired():
        print("Access token expired. Attempting to refresh...")
        try:
            tokens = refresh_token(REFRESH_TOKEN)
            print("Refreshed Tokens:", tokens)
            update_env(tokens)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise HTTPException(status_code=500, detail="Token refresh failed.")



def get_spotify_client():
    refresh_access_token_if_needed()
    print(f"Using token: {ACCESS_TOKEN}")
    return Spotify(auth=ACCESS_TOKEN)


@app.get("/access_token")
def access_token():
    """Provide the Spotify access token for Web Playback SDK."""
    global ACCESS_TOKEN, REFRESH_TOKEN
    try:
        # Refresh the access token if needed
        refresh_access_token_if_needed()
        if not ACCESS_TOKEN:
            raise HTTPException(status_code=500, detail="Access token is unavailable.")
        return {"token": ACCESS_TOKEN}
    except Exception as e:
        print(f"Error in /access_token: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve access token.")



@app.get("/")
def root():
    return {"message": "Spotify Wrapped Booster API"}

@app.get("/login")
def login():
    auth_url = get_auth_url()
    return {"auth_url": auth_url}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.lock = Lock()

    async def connect(self, websocket: WebSocket):
        async with self.lock:
            await websocket.accept()
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        async with self.lock:
            for connection in self.active_connections:
                await connection.send_text(message)

manager = ConnectionManager()

# Callback updates tokens and sends them via WebSocket
@app.get("/callback")
async def callback(code: str):
    try:
        tokens = get_tokens(code)
        update_env(tokens)
        set_token_expiry(tokens['expires_in'])
        # Notify clients to reload environment variables
        await manager.send_message("reload_env")  # Use await for async calls
        return {"message": "Tokens updated and notification sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/refresh")
def refresh_token_endpoint(request: Request):
    if not is_token_expired():
        return {"message": "Token is still valid"} 
    try:
        tokens = refresh_token(REFRESH_TOKEN)
        update_env(tokens)  # Saves tokens to .user
        set_token_expiry(tokens['expires_in'])
        return tokens
    except Exception as e:
        return RedirectResponse(url=f"/error?message={str(e)}")
    
# --- Playback Routes ---
@app.get("/devices")
def list_devices():
    """List all Spotify playback devices."""
    try:
        sp = get_spotify_client()
        devices = sp.devices()
        return {"devices": devices["devices"]}
    except SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/play")
def play_song(song_uri: str = None):
    """Start or resume playback."""
    try:
        sp = get_spotify_client()
        if song_uri:
            sp.start_playback(uris=[song_uri])
        else:
            sp.start_playback()
        return {"message": "Playback started"}
    except SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pause")
def pause_playback():
    """Pause current playback."""
    try:
        sp = get_spotify_client()
        sp.pause_playback()
        return {"message": "Playback paused"}
    except SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/volume")
def set_volume(volume_percent: int):
    """Set playback volume (0-100)."""
    try:
        if not (0 <= volume_percent <= 100):
            raise HTTPException(status_code=400, detail="Volume must be between 0 and 100.")
        sp = get_spotify_client()
        sp.volume(volume_percent)
        return {"message": f"Volume set to {volume_percent}%"}
    except SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/error")
def error(request: Request):
    error_message = request.query_params.get("message", "An error occurred")
    return {"message": error_message}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("WebSocket disconnected.")
        await manager.disconnect(websocket)  # Ensure disconnect is awaited
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect(websocket)  # Clean up on unexpected errors

@app.get("/sdk-client", response_class=HTMLResponse)
def sdk_client():
    """Serve the Spotify Web Playback SDK client page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spotify SDK Client</title>
        <script src="https://sdk.scdn.co/spotify-player.js"></script>
    </head>
    <body>
        <h1>Spotify Local Playback Client</h1>
        <button id="connect">Connect Spotify Player</button>
        <button id="play">Play</button>
        <button id="pause">Pause</button>
        <script>
            let player;

            window.onSpotifyWebPlaybackSDKReady = () => {
                player = new Spotify.Player({
                    name: 'Python Local Player',
                    getOAuthToken: callback => {
                        fetch('/access_token')
                            .then(response => response.json())
                            .then(data => callback(data.token));
                    },
                    volume: 0.8
                });

                // Error handling
                player.addListener('initialization_error', ({ message }) => console.error(message));
                player.addListener('authentication_error', ({ message }) => console.error(message));
                player.addListener('account_error', ({ message }) => console.error(message));
                player.addListener('playback_error', ({ message }) => console.error(message));

                // Playback status updates
                player.addListener('player_state_changed', state => {
                    console.log(state);
                });

                // Ready
                player.addListener('ready', ({ device_id }) => {
                    console.log('Ready with Device ID', device_id);
                });

                // Not Ready
                player.addListener('not_ready', ({ device_id }) => {
                    console.log('Device ID has gone offline', device_id);
                });

                // Connect the player
                player.connect();

                // Bind actions to buttons
                document.getElementById('connect').addEventListener('click', () => {
                    player.connect();
                });

                document.getElementById('play').addEventListener('click', () => {
                    player.resume();
                });

                document.getElementById('pause').addEventListener('click', () => {
                    player.pause();
                });
            };
        </script>
    </body>
    </html>
    """
    return html_content
