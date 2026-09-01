"""Esquemas Pydantic para las salidas estructuradas del LLM.

Cada esquema define el contrato exacto que Gemini debe devolver para
cada una de las 4 tareas de IA: clasificar, resumir, priorizar y redactar.
Se usan tanto para validar la respuesta del modelo como para generar
el `response_schema` que se le pasa a la API de Gemini.
"""
from pydantic import BaseModel, Field

from app.models.email import Categoria, Prioridad


class ClasificacionOutput(BaseModel):
    categoria: Categoria = Field(
        description="Categoría que mejor describe el correo."
    )
    confianza: float = Field(
        ge=0.0, le=1.0,
        description="Confianza del modelo en la categoría asignada, entre 0 y 1."
    )
    justificacion: str = Field(
        max_length=200,
        description="Explicación breve (1 frase) de por qué se asignó esta categoría."
    )


class ResumenOutput(BaseModel):
    resumen: str = Field(
        max_length=400,
        description="Resumen del contenido del correo en 2-3 frases, en español."
    )
    puntos_clave: list[str] = Field(
        default_factory=list,
        description="Hasta 3 puntos clave o acciones mencionadas en el correo."
    )


class PrioridadOutput(BaseModel):
    prioridad: Prioridad = Field(
        description="Nivel de urgencia/importancia del correo."
    )
    requiere_accion: bool = Field(
        description="True si el correo requiere que el usuario haga algo (responder, pagar, decidir)."
    )
    razon: str = Field(
        max_length=200,
        description="Explicación breve de por qué se asignó este nivel de prioridad."
    )


class BorradorOutput(BaseModel):
    aplica: bool = Field(
        description="True si tiene sentido generar un borrador de respuesta para este correo "
                     "(false para promociones, spam o correos informativos que no requieren respuesta)."
    )
    borrador: str = Field(
        default="",
        max_length=800,
        description="Borrador de respuesta sugerido, en tono profesional y breve. Vacío si aplica=false."
    )