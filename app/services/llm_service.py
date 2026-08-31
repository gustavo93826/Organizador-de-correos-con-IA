"""Servicio de integración con el LLM (Gemini).

Centraliza el cliente de Gemini y la función genérica para pedir
salidas estructuradas validadas con un esquema Pydantic.
"""
import json

from google import genai
from google.genai.errors import ClientError, ServerError
from loguru import logger
from pydantic import BaseModel
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import settings

MODEL = "gemini-3.6-flash"

_client: genai.Client | None = None


def get_gemini_client() -> genai.Client:
    """Devuelve un cliente de Gemini reutilizable (lazy singleton)."""
    global _client
    if _client is None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY no está configurada. Revisa tu archivo .env."
            )
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _es_error_reintentable(exc: BaseException) -> bool:
    """True si el error es transitorio y vale la pena reintentar.

    - ServerError (5xx): siempre transitorio, reintentar.
    - ClientError con code=429: rate limit / cuota agotada, reintentar
      con backoff. Otros errores 4xx (400, 401, 403...) son errores de
      programación o credenciales: NO tiene sentido reintentarlos.
    """
    if isinstance(exc, ServerError):
        return True
    if isinstance(exc, ClientError):
        return exc.code == 429
    return False


@retry(
    retry=retry_if_exception(_es_error_reintentable),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def llamar_llm_estructurado(prompt: str, esquema: type[BaseModel]) -> BaseModel:
    """Llama a Gemini pidiendo una respuesta que cumpla `esquema`.

    Ante un 429 (cuota agotada) o un error 5xx, reintenta automáticamente
    con backoff exponencial (2s, 4s, 8s... hasta 60s), hasta 5 intentos.
    Cualquier otro error (400, 401, 403) se relanza de inmediato.
    """
    client = get_gemini_client()

    logger.debug(f"Llamando a Gemini ({MODEL}) con esquema {esquema.__name__}...")

    chat = client.chats.create(model=MODEL)
    response = chat.send_message(
        prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": esquema,
        },
    )

    if response.parsed is not None:
        return response.parsed

    if response.text:
        try:
            payload = json.loads(response.text)
            return esquema.model_validate(payload)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Gemini no devolvió una respuesta válida para {esquema.__name__}: "
                f"{response.text}"
            ) from exc

    raise ValueError(
        f"Gemini no devolvió una respuesta válida para {esquema.__name__}: "
        f"{response.text}"
    )