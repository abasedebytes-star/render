from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import os

app = FastAPI()

FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # la URL de Render + /auth/facebook/callback


@app.get("/")
def home():
    return {"status": "ok", "message": "Facebook OAuth backend funcionando"}


@app.get("/auth/facebook/login")
def facebook_login():
    fb_auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={FB_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=public_profile,email"
        f"&response_type=code"
    )
    return RedirectResponse(fb_auth_url)


@app.get("/auth/facebook/callback")
def facebook_callback(code: str):
    token_url = (
        f"https://graph.facebook.com/v19.0/oauth/access_token"
        f"?client_id={FB_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&client_secret={FB_APP_SECRET}"
        f"&code={code}"
    )
    token_response = requests.get(token_url).json()

    if "access_token" not in token_response:
        return JSONResponse({"error": token_response}, status_code=400)

    user_info = requests.get(
        "https://graph.facebook.com/me",
        params={"fields": "id,name,email", "access_token": token_response["access_token"]}
    ).json()

    return user_info
