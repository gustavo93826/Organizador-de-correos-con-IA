"""Script manual para probar inserción y lectura en la base de datos.

Uso:
    uv run python -m scripts.probar_bd
"""
from datetime import datetime

from sqlmodel import Session, select

from app.core.database import engine
from app.models.email import Email

if __name__ == "__main__":
    with Session(engine) as session:
        # Insertar un correo de prueba (si no existe ya)
        existente = session.exec(
            select(Email).where(Email.gmail_id == "test-001")
        ).first()

        if not existente:
            correo = Email(
                gmail_id="test-001",
                remitente="alguien@ejemplo.com",
                asunto="Correo de prueba",
                cuerpo="Este es el cuerpo de un correo de prueba.",
                fecha_recibido=datetime.now(datetime.UTC),
            )
            session.add(correo)
            session.commit()
            session.refresh(correo)
            print(f"Correo insertado con id={correo.id}")
        else:
            print(f"El correo de prueba ya existía con id={existente.id}")

        # Leer todos los correos guardados
        todos = session.exec(select(Email)).all()
        print(f"\nTotal de correos en la base de datos: {len(todos)}")
        for c in todos:
            print(f"- [{c.estado_procesamiento}] {c.asunto} (de {c.remitente})")