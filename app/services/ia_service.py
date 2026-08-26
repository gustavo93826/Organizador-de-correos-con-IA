"""Las 4 funciones de IA del proyecto: clasificar, resumir, priorizar
y redactar. Cada una es independiente y reutilizable — reciben datos
simples (no dependen del modelo Email ni de la base de datos), lo que
las hace fáciles de probar y de encadenar más adelante en el workflow
del Paso 7.
"""
from app.models.email import Categoria
from app.models.schemas import (
    BorradorOutput,
    ClasificacionOutput,
    PrioridadOutput,
    ResumenOutput,
)
from app.services.llm_service import llamar_llm_estructurado

# Categorías para las que no tiene sentido generar un borrador de
# respuesta: ahorra llamadas al LLM (importante dado el free tier).
CATEGORIAS_SIN_BORRADOR = {Categoria.PROMOCIONES, Categoria.SPAM}


def clasificar_email(remitente: str, asunto: str, cuerpo: str) -> ClasificacionOutput:
    """Asigna una categoría al correo."""
    prompt = f"""Eres un asistente que clasifica correos electrónicos.
Clasifica el siguiente correo en una de estas categorías: trabajo, personal,
facturas, promociones, spam, otros.

De: {remitente}
Asunto: {asunto}
Cuerpo:
{cuerpo}
"""
    return llamar_llm_estructurado(prompt, ClasificacionOutput)


def resumir_email(remitente: str, asunto: str, cuerpo: str) -> ResumenOutput:
    """Genera un resumen breve y los puntos clave del correo."""
    prompt = f"""Resume el siguiente correo electrónico en 2-3 frases en español,
y extrae hasta 3 puntos clave o acciones mencionadas.

De: {remitente}
Asunto: {asunto}
Cuerpo:
{cuerpo}
"""
    return llamar_llm_estructurado(prompt, ResumenOutput)


def priorizar_email(
    remitente: str, asunto: str, cuerpo: str, categoria: Categoria
) -> PrioridadOutput:
    """Asigna un nivel de urgencia/importancia al correo.

    Recibe la categoría ya asignada porque ayuda al modelo a calibrar
    mejor la prioridad: una factura próxima a vencer no es lo mismo
    que una promoción.
    """
    prompt = f"""Eres un asistente que prioriza correos electrónicos para
un usuario ocupado. Evalúa la urgencia/importancia real del siguiente
correo, ya clasificado en la categoría "{categoria.value}".

De: {remitente}
Asunto: {asunto}
Cuerpo:
{cuerpo}

Considera: fechas límite mencionadas, si requiere una decisión o
respuesta, y si el remitente parece relevante (jefe, cliente, familia)
frente a un envío masivo/automatizado.
"""
    return llamar_llm_estructurado(prompt, PrioridadOutput)


def redactar_borrador(
    remitente: str, asunto: str, cuerpo: str, categoria: Categoria
) -> BorradorOutput:
    """Sugiere un borrador de respuesta, si el correo lo amerita.

    Para promociones y spam no llama al LLM: devuelve directamente
    aplica=False, ahorrando cuota del free tier en correos donde
    nunca tendría sentido responder.
    """
    if categoria in CATEGORIAS_SIN_BORRADOR:
        return BorradorOutput(aplica=False, borrador="")

    prompt = f"""Eres un asistente que redacta borradores de respuesta breves
y en tono profesional, en español.

De: {remitente}
Asunto: {asunto}
Cuerpo:
{cuerpo}

Si este correo realmente amerita una respuesta, redáctala (máximo 4
frases). Si es puramente informativo y no requiere respuesta, indica
aplica=false y deja el borrador vacío.
"""
    return llamar_llm_estructurado(prompt, BorradorOutput)