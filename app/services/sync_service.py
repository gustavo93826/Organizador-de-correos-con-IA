"""Sincroniza correos nuevos de Gmail hacia la base de datos local."""
from loguru import logger
from sqlmodel import Session, select

from app.core.database import engine
from app.models.email import Email
from app.services.gmail_service import get_gmail_service, obtener_mensajes_nuevos


def sincronizar_correos_nuevos(max_results: int = 10) -> int:
    """Trae los correos más recientes de Gmail y guarda como 'pendiente'
    los que todavía no existan en la base de datos.

    Devuelve la cantidad de correos nuevos guardados.
    """
    service = get_gmail_service()
    mensajes = obtener_mensajes_nuevos(service, max_results=max_results)

    nuevos = 0
    with Session(engine) as session:
        for datos in mensajes:
            existente = session.exec(
                select(Email).where(Email.gmail_id == datos["gmail_id"])
            ).first()
            if existente:
                continue
            session.add(Email(**datos))
            nuevos += 1
        session.commit()

    logger.info(f"Sincronización de Gmail: {nuevos} correo(s) nuevo(s) guardados.")
    return nuevos