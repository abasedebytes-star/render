[3:28 PM, 11/20/2025] Ivan Estigarribia: from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse, HTMLResponse
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
  …
[3:35 PM, 11/20/2025] Ivan Estigarribia: from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse, HTMLResponse
import requests
import os

app = FastAPI()

# ----------------------------------
# ENV VARIABLES (Render)
# ----------------------------------
FB_APP_ID = os.getenv("FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")          # Ej: https://tuapp.onrender.com/auth/facebook/callback
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")          # Para Webhooks


# ----------------------------------
# HOME
# ----------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "OAuth + Webhooks funcionando correctamente"
    }


# ----------------------------------
# FACEBOOK LOGIN
# ----------------------------------
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


# ----------------------------------
# WEBHOOK VERIFY (Facebook + Instagram)
# ----------------------------------
@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge, status_code=200)
    else:
        return PlainTextResponse("Token inválido", status_code=403)


# ----------------------------------
# WEBHOOK EVENTS
# ----------------------------------
@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.json()
    print("WEBHOOK DATA:", body)

    # Instagram y Facebook envían:
    # - mensajes
    # - comentarios
    # - eventos de media
    # - actualizaciones de cuenta

    return PlainTextResponse("OK", status_code=200)


# ----------------------------------
# PRIVACY POLICY (Facebook Requirement)
# ----------------------------------
@app.get("/privacy-policy", response_class=HTMLResponse)
def privacy_policy():
    return """
    <html><body>
    <h1>Política de Privacidad</h1>
    <p>Esta aplicación utiliza datos proporcionados por Facebook e Instagram únicamente para permitir el inicio de sesión, verificar identidad y recibir notificaciones mediante webhooks.</p>

    <h2>1. Datos que recopilamos</h2>
    <p>- ID de usuario de Facebook/Instagram<br>
    - Nombre y correo electrónico (solo si el usuario los autoriza)<br>
    - Información enviada por los webhooks de Meta (mensajes, comentarios, eventos de cuenta, etc.)</p>

    <h2>2. Cómo usamos los datos</h2>
    <p>Los datos se utilizan únicamente para:</p>
    <p>- Autenticar al usuario<br>
    - Permitir funcionamiento de la integración<br>
    - Procesar eventos enviados por los servicios de Meta</p>

    <h2>3. No compartimos datos</h2>
    <p>No vendemos, transferimos ni compartimos información con terceros.</p>

    <h2>4. Seguridad</h2>
    <p>Los datos son procesados de forma segura y nunca se almacenan de manera permanente.</p>

    <h2>5. Contacto</h2>
    <p>Si necesitás más información, podés enviar un mensaje.</p>
    </body></html>
    """


# ----------------------------------
# DATA DELETION (Facebook Requirement)
# ----------------------------------
@app.get("/data-deletion", response_class=HTMLResponse)
def data_deletion():
    return """
    <html><body>
    <h1>Eliminación de Datos del Usuario</h1>
    <p>Si desea eliminar su información asociada a esta aplicación, siga uno de los siguientes pasos:</p>

    <h2>1. Eliminación automática</h2>
    <p>La aplicación no almacena información personal en bases de datos. Todos los datos obtenidos desde Facebook se eliminan automáticamente cuando el usuario revoca permisos desde:</p>
    <p><strong>Facebook Settings → Apps and Websites</strong></p>

    <h2>2. Solicitud manual</h2>
    <p>Si desea solicitar la eliminación inmediata de cualquier dato temporal procesado, puede contactarnos y se eliminará en un plazo de 48 horas.</p>

    <h2>3. Webhooks</h2>
    <p>Los datos enviados por Facebook/Instagram a través de webhooks no se almacenan. Solo se procesan en tiempo real para funcionamiento del sistema.</p>
    </body></html>
    """
