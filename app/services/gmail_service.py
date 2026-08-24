"""Servicio de autenticación y acceso a la API de Gmail.

Implementa el flujo OAuth2 "installed app": la primera vez abre el
navegador para pedir consentimiento, y las siguientes veces reutiliza
el token guardado en disco (refrescándolo automáticamente si expiró).
"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

from app.core.config import settings

# Con .readonly nos basta para leer y clasificar correos.
# Lo ampliaremos a gmail.modify más adelante si queremos
# archivar/etiquetar automáticamente.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Devuelve un cliente autenticado de la API de Gmail."""
    creds = None
    token_path = settings.gmail_token_path

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Token expirado, refrescando...")
            creds.refresh(Request())
        else:
            logger.info("No hay token válido, iniciando flujo de consentimiento OAuth2...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.gmail_credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json())
        logger.info(f"Token guardado en {token_path}")

    return build("gmail", "v1", credentials=creds)


def list_recent_messages(service, max_results: int = 5) -> list[dict]:
    """Devuelve los últimos `max_results` correos con remitente y asunto."""
    response = service.users().messages().list(
        userId="me", maxResults=max_results
    ).execute()

    messages = []
    for msg_ref in response.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["Subject", "From"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        messages.append({
            "id": msg["id"],
            "from": headers.get("From", "(desconocido)"),
            "subject": headers.get("Subject", "(sin asunto)"),
        })

    return messages