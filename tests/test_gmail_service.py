"""Pruebas del manejo de errores en la autenticación con Gmail."""
import pytest

from app.services.gmail_service import get_gmail_service


def test_get_gmail_service_falla_con_mensaje_claro_si_faltan_credenciales(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "app.services.gmail_service.settings.gmail_credentials_path", tmp_path / "no-existe.json"
    )
    monkeypatch.setattr(
        "app.services.gmail_service.settings.gmail_token_path", tmp_path / "no-existe-token.json"
    )

    with pytest.raises(FileNotFoundError, match="credenciales de Gmail"):
        get_gmail_service()