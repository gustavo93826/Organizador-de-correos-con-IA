"""Esquemas de entrada/salida de la API (distintos de los esquemas de
salida del LLM en app/models/schemas.py)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.email import Categoria, EstadoProcesamiento, Prioridad


class EmailListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    remitente: str
    asunto: str
    categoria: Categoria | None
    prioridad: Prioridad | None
    estado_procesamiento: EstadoProcesamiento
    fecha_recibido: datetime


class EmailDetail(EmailListItem):
    cuerpo: str
    resumen: str | None
    borrador_respuesta: str | None


class ActualizarBorrador(BaseModel):
    borrador: str