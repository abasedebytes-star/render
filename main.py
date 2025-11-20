from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse
import requests
import os

app = FastAPI()

# Facebook OAuth
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # https://render-xxxx.onrender.com/auth/facebook/callback

# Webhooks (Facebook + Instagram)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")


# ---------------------------
# HOME
# ---------------------------
@app.get("/")
def home():
    return {"status": "ok", "message": "OAuth + Webhooks funcionando"}


# ---------------------------
# FACEBOOK LOGIN
# ---------------------------
@app.get("/auth/facebook/login")
def facebook_login():
    fb_auth_url = (
        "https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={FB_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=public_profile,email"
        f"&response_type=code"
    )
    return RedirectResponse(fb_auth_url)


@app.get("/auth/facebook/callback")
def facebook_callback(code: str):
    token_url = (
        "https://graph.facebook.com/v19.0/oauth/access_token"
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
        params={
            "fields": "id,name,email",
            "access_token": token_response["access_token"]
        }
    ).json()

    return user_info


# ---------------------------
# WEBHOOK (Facebook + Instagram)
# ---------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge, status_code=200)
    else:
        return PlainTextResponse("Token inválido", status_code=403)


@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()
    print("WEBHOOK DATA:", body)

    # ⚠️ IMPORTANTE: Instagram también envía aquí sus eventos
    # Ej: comentarios, mensajes, cambios en medios, etc.

    return PlainTextResponse("OK", status_code=200)
