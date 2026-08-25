"""Configuración del motor de base de datos y gestión de sesiones."""
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# check_same_thread=False es necesario porque SQLite por defecto solo
# permite acceso desde el hilo que abrió la conexión, y FastAPI/APScheduler
# usarán varios hilos.
engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Crea todas las tablas definidas con SQLModel si no existen aún."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Generador de sesión para inyección de dependencias (FastAPI)."""
    with Session(engine) as session:
        yield session