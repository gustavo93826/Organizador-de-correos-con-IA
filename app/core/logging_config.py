"""Configuración centralizada de logging con Loguru.

Reemplaza el sink por defecto de Loguru (solo consola) por dos sinks:
uno a consola (para desarrollo) y uno a archivo rotativo (para poder
revisar qué pasó después, sin tener la terminal abierta).
"""
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings

LOGS_DIR = Path("logs")


def configurar_logging() -> None:
    """Configura los sinks de Loguru. Debe llamarse una sola vez, al
    arrancar la aplicación (ver app/main.py)."""
    LOGS_DIR.mkdir(exist_ok=True)

    logger.remove()  # quita el sink por defecto para controlar el formato

    logger.add(
        sys.stderr,
        level=settings.log_level,
        colorize=True,
        format=(
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        ),
    )

    logger.add(
        LOGS_DIR / "app.log",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {module}:{function}:{line} - {message}",
        backtrace=False,
        # diagnose=False evita que Loguru filtre valores de variables locales
        # en los tracebacks -- importante porque esas variables pueden
        # contener contenido de correos o la API key.
        diagnose=False,
    )

    logger.info(f"Logging configurado (nivel={settings.log_level}, archivo={LOGS_DIR / 'app.log'})")