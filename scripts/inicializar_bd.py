"""Script manual para crear las tablas de la base de datos.

Uso:
    uv run python -m scripts.inicializar_bd  
"""
from app.core.database import create_db_and_tables
from app.models.email import Email  # noqa: F401  (registra el modelo en metadata)

if __name__ == "__main__":
    create_db_and_tables()
    print("Tablas creadas correctamente en la base de datos.")