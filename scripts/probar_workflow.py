"""Script manual para probar el workflow completo de Prefect.

Uso:
    uv run python -m scripts.probar_workflow
"""
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.database import engine
from app.models.email import Email
from app.workflows.procesar_email import procesar_bandeja

CORREOS_DE_PRUEBA = [
    {
        "gmail_id": "workflow-test-001",
        "remitente": "ana.gomez@miempresa.com",
        "asunto": "Reunión de equipo - confirmar asistencia",
        "cuerpo": "¿Podrías confirmar tu asistencia a la reunión del jueves a las 10am?",
    },
    {
        "gmail_id": "workflow-test-002",
        "remitente": "ofertas@tiendaonline.com",
        "asunto": "50% de descuento solo hoy",
        "cuerpo": "Aprovecha nuestro descuento exclusivo de 50% en toda la tienda.",
    },
]

if __name__ == "__main__":
    with Session(engine) as session:
        for datos in CORREOS_DE_PRUEBA:
            existente = session.exec(
                select(Email).where(Email.gmail_id == datos["gmail_id"])
            ).first()
            if not existente:
                session.add(Email(fecha_recibido=datetime.now(timezone.utc), **datos))
        session.commit()

    print("Ejecutando el flujo 'procesar-bandeja'...\n")
    procesar_bandeja(limite=10)

    print("\nResultado en la base de datos:\n")
    with Session(engine) as session:
        correos = session.exec(select(Email)).all()
        for c in correos:
            print(
                f"- [{c.estado_procesamiento}] {c.asunto} | "
                f"categoria={c.categoria} | prioridad={c.prioridad}"
            )