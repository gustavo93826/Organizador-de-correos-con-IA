"""Fixtures compartidas: motor de base de datos en memoria y cliente
de pruebas de FastAPI con la sesión sobreescrita.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.main import app


class _SchedulerFalso:
    """Reemplaza al scheduler real durante los tests: no debe intentar
    conectarse a Gmail ni a Gemini cada vez que se crea un TestClient."""

    def start(self):
        pass

    def shutdown(self):
        pass


@pytest.fixture(name="engine_test")
def engine_test_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine_test):
    with Session(engine_test) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session, monkeypatch):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    monkeypatch.setattr("app.main.crear_scheduler", lambda: _SchedulerFalso())

    # raise_server_exceptions=False:  probar el comportamiento real
    # de producción, donde el manejador global convierte una excepción no
    # controlada en una respuesta 500 en vez de relanzarla (que es lo que
    # el TestClient hace por defecto, pensado para depurar).
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

    app.dependency_overrides.clear()