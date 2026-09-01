"""Modelo de datos principal: representa un correo y todo lo que
la IA produce sobre él (categoría, resumen, prioridad, borrador).
"""
from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class Categoria(str, Enum):
    TRABAJO = "trabajo"
    PERSONAL = "personal"
    FACTURAS = "facturas"
    PROMOCIONES = "promociones"
    SPAM = "spam"
    OTROS = "otros"


class Prioridad(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class EstadoProcesamiento(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


class Email(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Identificador único de Gmail: evita procesar el mismo correo dos veces
    gmail_id: str = Field(index=True, unique=True)

    remitente: str
    asunto: str
    cuerpo: str
    fecha_recibido: datetime

    # Campos que rellenará la IA (empiezan vacíos)
    categoria: Categoria | None = Field(default=None)
    resumen: str | None = Field(default=None)
    prioridad: Prioridad | None = Field(default=None)
    borrador_respuesta: str | None = Field(default=None)

    estado_procesamiento: EstadoProcesamiento = Field(default=EstadoProcesamiento.PENDIENTE)

    creado_en: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actualizado_en: datetime = Field(default_factory=lambda: datetime.now(UTC))