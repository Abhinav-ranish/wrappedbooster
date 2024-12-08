import asyncio
from asyncio import Lock
from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from auth import get_auth_url, get_tokens, refresh_token
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from pathlib import Path

dotenv_path = Path(__file__).parent.parent / ".user"  # Adjust for relative paths
load_dotenv(dotenv_path)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
EXPIRES_IN = os.getenv("EXPIRES_IN")

TOKEN_EXPIRY_TIME = None  # Tracks token expiry time

def update_env(tokens):
    try:
        dotenv_path = Path(__file__).parent.parent / ".user"
        with open(dotenv_path, "w") as f:
            f.write(f"ACCESS_TOKEN={tokens['access_token']}\n")
            f.write(f"REFRESH_TOKEN={tokens['refresh_token']}\n")
            f.write(f"EXPIRES_IN={tokens['expires_in']}\n")
        print(f"Updated tokens in {dotenv_path}")
    except Exception as e:
        print(f"Error updating tokens: {e}")


def is_token_expired():
    global TOKEN_EXPIRY_TIME
    if TOKEN_EXPIRY_TIME is None:
        return True
    return datetime.now() >= TOKEN_EXPIRY_TIME

def set_token_expiry(expires_in):
    global TOKEN_EXPIRY_TIME
    TOKEN_EXPIRY_TIME = datetime.now() + timedelta(seconds=int(expires_in))

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Spotify Wrapped Booster API"}

@app.get("/login")
def login():
    auth_url = get_auth_url()
    return {"auth_url": auth_url}
    # return RedirectResponse(url=auth_url)


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

