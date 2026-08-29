"""Punto de entrada de la aplicación FastAPI.

Además de exponer la API REST, en el ciclo de vida de la app se
inicializan las tablas de la base de datos y se arranca el scheduler
de APScheduler (Paso 8), para que la sincronización y el procesamiento
periódico corran automáticamente mientras el servidor esté vivo.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.emails import router as emails_router
from app.core.database import create_db_and_tables
from app.core.scheduler import crear_scheduler
from app.models.email import Email  # noqa: F401  (registra el modelo en metadata)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación...")
    create_db_and_tables()

    scheduler = crear_scheduler()
    scheduler.start()
    logger.info("Scheduler iniciado junto con la API.")

    yield

    logger.info("Apagando scheduler...")
    scheduler.shutdown()


app = FastAPI(title="Organizador de correos con IA", lifespan=lifespan)
app.include_router(emails_router)


@app.get("/health")
def health():
    return {"status": "ok"}