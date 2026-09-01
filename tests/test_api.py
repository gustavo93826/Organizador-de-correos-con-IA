"""Pruebas de integración de los endpoints de la API (Paso 9)."""
from datetime import UTC, datetime

from sqlmodel import Session

from app.models.email import Categoria, Email, EstadoProcesamiento, Prioridad


def _crear_email(session: Session, **overrides) -> Email:
    datos = {
        "gmail_id": "test-api-001",
        "remitente": "alguien@ejemplo.com",
        "asunto": "Correo de prueba",
        "cuerpo": "Cuerpo de prueba",
        "fecha_recibido": datetime.now(UTC),
        "estado_procesamiento": EstadoProcesamiento.COMPLETADO,
        "categoria": Categoria.TRABAJO,
        "prioridad": Prioridad.ALTA,
        "resumen": "Un resumen de prueba.",
        "borrador_respuesta": "Borrador original.",
    }
    datos.update(overrides)
    email = Email(**datos)
    session.add(email)
    session.commit()
    session.refresh(email)
    return email


def test_listar_emails_vacio(client):
    respuesta = client.get("/emails")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_emails_con_datos(client, session):
    _crear_email(session)
    respuesta = client.get("/emails")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert len(datos) == 1
    assert datos[0]["asunto"] == "Correo de prueba"


def test_listar_emails_filtra_por_categoria(client, session):
    _crear_email(session, gmail_id="a", categoria=Categoria.TRABAJO)
    _crear_email(session, gmail_id="b", categoria=Categoria.PROMOCIONES)

    respuesta = client.get("/emails", params={"categoria": "trabajo"})
    datos = respuesta.json()
    assert len(datos) == 1
    assert datos[0]["categoria"] == "trabajo"


def test_obtener_email_no_encontrado(client):
    respuesta = client.get("/emails/999")
    assert respuesta.status_code == 404


def test_actualizar_borrador(client, session):
    email = _crear_email(session)
    respuesta = client.patch(
        f"/emails/{email.id}/borrador", json={"borrador": "Nuevo borrador editado a mano."}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["borrador_respuesta"] == "Nuevo borrador editado a mano."


def test_reprocesar_email(client, session, mocker):
    email = _crear_email(session, estado_procesamiento=EstadoProcesamiento.COMPLETADO)

    mock_procesar = mocker.patch("app.api.emails.procesar_un_email")

    respuesta = client.post(f"/emails/{email.id}/reprocesar")
    assert respuesta.status_code == 202
    mock_procesar.assert_called_once_with(email.id)