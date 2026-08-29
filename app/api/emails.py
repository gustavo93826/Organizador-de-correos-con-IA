"""Endpoints REST para consultar y gestionar los correos procesados."""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.api.schemas import ActualizarBorrador, EmailDetail, EmailListItem
from app.core.database import get_session
from app.models.email import Categoria, Email, EstadoProcesamiento, Prioridad
from app.workflows.procesar_email import procesar_un_email

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("", response_model=list[EmailListItem])
def listar_emails(
    categoria: Categoria | None = None,
    prioridad: Prioridad | None = None,
    estado: EstadoProcesamiento | None = None,
    session: Session = Depends(get_session),
):
    """Lista correos, opcionalmente filtrados por categoría, prioridad o estado."""
    query = select(Email)
    if categoria:
        query = query.where(Email.categoria == categoria)
    if prioridad:
        query = query.where(Email.prioridad == prioridad)
    if estado:
        query = query.where(Email.estado_procesamiento == estado)

    query = query.order_by(Email.fecha_recibido.desc())
    return session.exec(query).all()


@router.get("/{email_id}", response_model=EmailDetail)
def obtener_email(email_id: int, session: Session = Depends(get_session)):
    email = session.get(Email, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Correo no encontrado")
    return email


@router.patch("/{email_id}/borrador", response_model=EmailDetail)
def actualizar_borrador(
    email_id: int,
    datos: ActualizarBorrador,
    session: Session = Depends(get_session),
):
    """Permite editar manualmente el borrador de respuesta sugerido por la IA."""
    email = session.get(Email, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Correo no encontrado")

    email.borrador_respuesta = datos.borrador
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


@router.post("/{email_id}/reprocesar", status_code=202)
def reprocesar_email(
    email_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    """Fuerza el reprocesamiento de un correo puntual, en segundo plano.

    A diferencia del scheduler del Paso 8 (que corre por intervalo fijo),
    esto usa BackgroundTasks de FastAPI para no bloquear la respuesta
    HTTP mientras el LLM procesa el correo (puede tardar varios segundos).
    """
    email = session.get(Email, email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Correo no encontrado")

    email.estado_procesamiento = EstadoProcesamiento.PROCESANDO
    session.add(email)
    session.commit()

    background_tasks.add_task(procesar_un_email, email_id)
    return {"mensaje": f"Reprocesamiento del correo {email_id} iniciado en segundo plano."}