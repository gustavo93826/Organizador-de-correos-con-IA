"""Pruebas del workflow de Prefect, con las llamadas al LLM
mockeadas para no gastar cuota real de Gemini durante los tests."""
from datetime import UTC, datetime

import pytest
from prefect.testing.utilities import prefect_test_harness
from sqlmodel import Session

from app.models.email import Categoria, Email, EstadoProcesamiento, Prioridad
from app.models.schemas import BorradorOutput, ClasificacionOutput, PrioridadOutput, ResumenOutput
from app.workflows.procesar_email import procesar_un_email


@pytest.fixture(scope="module", autouse=True)
def prefect_test_server():
    with prefect_test_harness():
        yield


def _insertar_email_pendiente(engine, gmail_id="wf-001") -> int:
    with Session(engine) as session:
        email = Email(
            gmail_id=gmail_id,
            remitente="ana@empresa.com",
            asunto="Reunión mañana",
            cuerpo="¿Puedes confirmar tu asistencia?",
            fecha_recibido=datetime.now(UTC),
        )
        session.add(email)
        session.commit()
        session.refresh(email)
        return email.id


def test_procesar_un_email_completa_correctamente(monkeypatch, engine_test, mocker):
    monkeypatch.setattr("app.workflows.procesar_email.engine", engine_test)
    email_id = _insertar_email_pendiente(engine_test)

    mocker.patch(
        "app.workflows.procesar_email.clasificar_email",
        return_value=ClasificacionOutput(categoria=Categoria.TRABAJO, confianza=0.9, justificacion="test"),
    )
    mocker.patch(
        "app.workflows.procesar_email.resumir_email",
        return_value=ResumenOutput(resumen="Resumen de prueba.", puntos_clave=["Confirmar asistencia"]),
    )
    mocker.patch(
        "app.workflows.procesar_email.priorizar_email",
        return_value=PrioridadOutput(prioridad=Prioridad.ALTA, requiere_accion=True, razon="test"),
    )
    mocker.patch(
        "app.workflows.procesar_email.redactar_borrador",
        return_value=BorradorOutput(aplica=True, borrador="Confirmo mi asistencia."),
    )

    procesar_un_email(email_id)

    with Session(engine_test) as session:
        email = session.get(Email, email_id)
        assert email.estado_procesamiento == EstadoProcesamiento.COMPLETADO
        assert email.categoria == Categoria.TRABAJO
        assert email.prioridad == Prioridad.ALTA
        assert email.borrador_respuesta == "Confirmo mi asistencia."


def test_procesar_un_email_marca_error_si_falla_el_llm(monkeypatch, engine_test, mocker):
    monkeypatch.setattr("app.workflows.procesar_email.engine", engine_test)
    email_id = _insertar_email_pendiente(engine_test, gmail_id="wf-002")

    mocker.patch(
        "app.workflows.procesar_email.clasificar_email",
        side_effect=RuntimeError("Fallo simulado del LLM"),
    )

    with pytest.raises(RuntimeError):
        procesar_un_email(email_id)

    with Session(engine_test) as session:
        email = session.get(Email, email_id)
        assert email.estado_procesamiento == EstadoProcesamiento.ERROR