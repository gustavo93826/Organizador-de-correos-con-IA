"""Script manual para correr el scheduler de forma standalone.

Uso:
    uv run python -m scripts.iniciar_scheduler

Detén con Ctrl+C.
"""
import time

from loguru import logger

from app.core.scheduler import crear_scheduler

if __name__ == "__main__":
    scheduler = crear_scheduler()
    scheduler.start()
    logger.info("Scheduler iniciado. Presiona Ctrl+C para detener.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Deteniendo scheduler...")
        scheduler.shutdown()