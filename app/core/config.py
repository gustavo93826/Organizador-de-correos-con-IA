"""Configuración centralizada de la aplicación.

Carga las variables de entorno definidas en `.env` y las expone
de forma validada a través de la clase `Settings`.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gmail_credentials_path: Path = Field(
        default_factory=lambda: Path(os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"))
    )
    gmail_token_path: Path = Field(
        default_factory=lambda: Path(os.getenv("GMAIL_TOKEN_PATH", "token.json"))
    )
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./data/organizador.db")
    )
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


settings = Settings()