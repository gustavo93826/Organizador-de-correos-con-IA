"""Workflow de Prefect que encadena clasificar → resumir → priorizar →
redactar para los correos pendientes de la base de datos.
"""
from datetime import datetime, timezone

from prefect import flow, get_run_logger, task
from prefect.tasks import exponential_backoff
from sqlmodel import Session, select

from app.core.database import engine
from app.models.email import Email, EstadoProcesamiento
from app.services.ia_service import (
    clasificar_email,
    priorizar_email,
    redactar_borrador,
    resumir_email,
)

# --- Tareas de lectura/escritura en BD ---
# Retries con backoff: protegen contra problemas transitorios de la
# base de datos (p. ej. "database is locked" cuando el scheduler del
# Paso 8 y la futura API del Paso 9 acceden casi al mismo tiempo).


@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=2), retry_jitter_factor=0.5)
def obtener_ids_pendientes(limite: int) -> list[int]:
    with Session(engine) as session:
        ids = session.exec(
            select(Email.id)
            .where(Email.estado_procesamiento == EstadoProcesamiento.PENDIENTE)
            .limit(limite)
        ).all()
        return list(ids)


@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=2), retry_jitter_factor=0.5)
def obtener_datos_email(email_id: int) -> dict:
    with Session(engine) as session:
        email = session.get(Email, email_id)
        if email is None:
            raise ValueError(f"No existe un correo con id={email_id}")
        return {"remitente": email.remitente, "asunto": email.asunto, "cuerpo": email.cuerpo}


@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=2), retry_jitter_factor=0.5)
def guardar_resultados(email_id, categoria, resumen, prioridad, borrador) -> None:
    with Session(engine) as session:
        email = session.get(Email, email_id)
        email.categoria = categoria
        email.resumen = resumen
        email.prioridad = prioridad
        email.borrador_respuesta = borrador
        email.estado_procesamiento = EstadoProcesamiento.COMPLETADO
        email.actualizado_en = datetime.now(timezone.utc)
        session.add(email)
        session.commit()


@task(retries=3, retry_delay_seconds=exponential_backoff(backoff_factor=2), retry_jitter_factor=0.5)
def marcar_como_error(email_id: int) -> None:
    with Session(engine) as session:
        email = session.get(Email, email_id)
        if email:
            email.estado_procesamiento = EstadoProcesamiento.ERROR
            email.actualizado_en = datetime.now(timezone.utc)
            session.add(email)
            session.commit()


# --- Tareas que llaman al LLM ---
# retries=0 a propósito: `llamar_llm_estructurado` (Paso 5) ya reintenta
# internamente con tenacity ante 429/5xx. Ver nota arriba.


@task(retries=0)
def clasificar_task(datos: dict):
    return clasificar_email(**datos)


@task(retries=0)
def resumir_task(datos: dict):
    return resumir_email(**datos)


@task(retries=0)
def priorizar_task(datos: dict, categoria):
    return priorizar_email(**datos, categoria=categoria)


@task(retries=0)
def redactar_task(datos: dict, categoria):
    return redactar_borrador(**datos, categoria=categoria)


# --- Flujos ---


@flow(name="procesar-un-email")
def procesar_un_email(email_id: int) -> None:
    """Encadena las 4 tareas de IA para un solo correo y persiste el resultado.

    Si algo falla en cualquier punto, el correo queda marcado como ERROR
    en vez de quedarse en un estado ambiguo, y se relanza la excepción
    para que quede registrada como fallo en Prefect.
    """
    logger_prefect = get_run_logger()
    try:
        datos = obtener_datos_email(email_id)

        clasificacion = clasificar_task(datos)
        resumen = resumir_task(datos)
        prioridad = priorizar_task(datos, clasificacion.categoria)
        borrador = redactar_task(datos, clasificacion.categoria)

        guardar_resultados(
            email_id=email_id,
            categoria=clasificacion.categoria,
            resumen=resumen.resumen,
            prioridad=prioridad.prioridad,
            borrador=borrador.borrador,
        )
        logger_prefect.info(f"Correo {email_id} procesado correctamente.")
    except Exception:
        logger_prefect.exception(f"Error procesando el correo {email_id}.")
        marcar_como_error(email_id)
        raise


@flow(name="procesar-bandeja")
def procesar_bandeja(limite: int = 10) -> None:
    """Flujo principal: procesa hasta `limite` correos pendientes.

    Este es el flujo que el Paso 8 disparará periódicamente con
    APScheduler. Si un correo falla, no detiene a los demás.
    """
    logger_prefect = get_run_logger()
    ids = obtener_ids_pendientes(limite)
    logger_prefect.info(f"{len(ids)} correo(s) pendientes por procesar.")

    for email_id in ids:
        try:
            procesar_un_email(email_id)
        except Exception:
            # Ya quedó marcado como ERROR dentro de procesar_un_email;
            # seguimos con el resto de la bandeja.
            continue