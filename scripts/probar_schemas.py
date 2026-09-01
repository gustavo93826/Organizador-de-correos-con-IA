"""Script manual para validar que los esquemas Pydantic funcionan
correctamente antes de conectarlos con el LLM.

Uso:
    uv run python -m scripts.probar_schemas
"""
from pydantic import ValidationError

from app.models.schemas import (
    BorradorOutput,
    ClasificacionOutput,
    PrioridadOutput,
    ResumenOutput,
)

# --- Casos válidos, simulando lo que debería devolver el LLM ---

clasificacion = ClasificacionOutput(
    categoria="trabajo",
    confianza=0.92,
    justificacion="Menciona una reunión de equipo y un deadline de proyecto.",
)
print("Clasificación válida:", clasificacion.model_dump())

resumen = ResumenOutput(
    resumen="El remitente pide confirmar la asistencia a la reunión del jueves y adjunta la agenda.",
    puntos_clave=["Confirmar asistencia", "Revisar agenda adjunta"],
)
print("\nResumen válido:", resumen.model_dump())

prioridad = PrioridadOutput(
    prioridad="alta",
    requiere_accion=True,
    razon="Pide una respuesta antes del jueves.",
)
print("\nPrioridad válida:", prioridad.model_dump())

borrador = BorradorOutput(
    aplica=True,
    borrador="Hola, confirmo mi asistencia a la reunión del jueves. Saludos.",
)
print("\nBorrador válido:", borrador.model_dump())

# --- Caso inválido a propósito, para confirmar que la validación funciona ---

print("\nProbando un caso inválido (categoría inexistente)...")
try:
    ClasificacionOutput(
        categoria="deportes",  # no existe en el enum Categoria
        confianza=0.5,
        justificacion="Prueba de error.",
    )
except ValidationError as e:
    print("Validación funcionó correctamente, error capturado:")
    print(e)