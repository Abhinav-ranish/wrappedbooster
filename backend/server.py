from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from auth import get_auth_url, get_tokens, refresh_token
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
EXPIRES_IN = os.getenv("EXPIRES_IN")
TOKEN_EXPIRY_TIME = None  # Tracks token expiry time

def update_env(tokens):
    with open(".env", "w") as f:
        f.write(f"ACCESS_TOKEN={tokens['access_token']}\n")
        f.write(f"REFRESH_TOKEN={tokens['refresh_token']}\n")
        f.write(f"EXPIRES_IN={tokens['expires_in']}\n")

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
    return RedirectResponse(url=auth_url)

@app.get("/callback")
def callback(code: str):
    try:
        tokens = get_tokens(code)
        update_env(tokens)
        set_token_expiry(tokens['expires_in'])
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_in": tokens["expires_in"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/refresh")
def refresh_token_endpoint(request: Request):
    if is_token_expired():
        try:
            tokens = refresh_token(REFRESH_TOKEN)
            update_env(tokens)
            set_token_expiry(tokens['expires_in'])
            return tokens
        except Exception as e:
            return RedirectResponse(url=f"/error?message={str(e)}")
    return {"message": "Token is still valid"}

@app.get("/error")
def error(request: Request):
    error_message = request.query_params.get("message", "An error occurred")
    return {"message": error_message}
