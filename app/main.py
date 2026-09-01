"""Punto de entrada de la aplicación FastAPI.

Además de exponer la API REST, en el ciclo de vida de la app se
inicializan las tablas de la base de datos y se arranca el scheduler
de APScheduler, para que la sincronización y el procesamiento
periódico corran automáticamente mientras el servidor esté vivo.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger


from app.api.emails import router as emails_router
from app.core.database import create_db_and_tables
from app.core.logging_config import configurar_logging
from app.core.scheduler import crear_scheduler
from app.models.email import Email  # noqa: F401  (registra el modelo en metadata)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configurar_logging()
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

@app.exception_handler(Exception)
async def manejador_global_de_errores(request: Request, exc: Exception):
    """Captura cualquier excepción no manejada por un endpoint, la
    registra con contexto (método + ruta) y devuelve una respuesta
    genérica en vez de un traceback crudo al cliente.
    """
    logger.exception(f"Error no controlado en {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno. Revisa los logs para más detalle."},
    )



@app.get("/health")
def health():
    return {"status": "ok"}