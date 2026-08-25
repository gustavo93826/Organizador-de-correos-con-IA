"""Script manual para validar la conexión OAuth2 con Gmail.

Uso:
    uv run python -m scripts.probar_conexion_gmail
"""
from app.services.gmail_service import get_gmail_service, list_recent_messages

if __name__ == "__main__":
    service = get_gmail_service()
    correos = list_recent_messages(service, max_results=5)

    print(f"\nConexión exitosa. Últimos {len(correos)} correos:\n")
    for c in correos:
        print(f"- De: {c['from']}\n  Asunto: {c['subject']}\n")