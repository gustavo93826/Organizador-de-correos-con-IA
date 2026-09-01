"""Script manual para probar las 4 funciones de IA por separado,
todavía sin encadenarlas.

Uso:
    uv run python -m scripts.probar_ia
"""
from app.services.ia_service import (
    clasificar_email,
    priorizar_email,
    redactar_borrador,
    resumir_email,
)

CORREOS_DE_PRUEBA = [
    {
        "remitente": "facturacion@electricidad-ejemplo.com",
        "asunto": "Tu factura de agosto ya está disponible",
        "cuerpo": (
            "Tu factura de electricidad correspondiente a agosto de 2026 ya "
            "está disponible. El monto a pagar es de $842 MXN, con "
            "vencimiento el 5 de septiembre."
        ),
    },
    {
        "remitente": "ana.gomez@miempresa.com",
        "asunto": "Reunión de equipo - confirmar asistencia",
        "cuerpo": (
            "Hola, ¿podrías confirmar tu asistencia a la reunión de equipo "
            "del jueves a las 10am? Necesitamos revisar el estado del "
            "proyecto antes del deadline del viernes."
        ),
    },
    {
        "remitente": "ofertas@tiendaonline.com",
        "asunto": "50% de descuento solo hoy",
        "cuerpo": "Aprovecha nuestro descuento exclusivo de 50% en toda la tienda, solo por hoy.",
    },
]

if __name__ == "__main__":
    for correo in CORREOS_DE_PRUEBA:
        print("=" * 70)
        print(f"De: {correo['remitente']}\nAsunto: {correo['asunto']}\n")

        clasificacion = clasificar_email(**correo)
        print(f"[Clasificación] {clasificacion.model_dump()}")

        resumen = resumir_email(**correo)
        print(f"[Resumen] {resumen.model_dump()}")

        prioridad = priorizar_email(**correo, categoria=clasificacion.categoria)
        print(f"[Prioridad] {prioridad.model_dump()}")

        borrador = redactar_borrador(**correo, categoria=clasificacion.categoria)
        print(f"[Borrador] {borrador.model_dump()}")

        print()