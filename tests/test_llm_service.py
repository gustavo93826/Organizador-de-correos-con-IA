from app.models.schemas import ResumenOutput
from app.services.llm_service import llamar_llm_estructurado


class DummyResponse:
    def __init__(self, *, text: str | None = None, parsed=None):
        self.text = text
        self.parsed = parsed


class DummyChat:
    def send_message(self, prompt: str, config=None):
        assert config is not None
        assert config["response_mime_type"] == "application/json"
        assert config["response_schema"] is ResumenOutput
        return DummyResponse(
            text='{"resumen": "Resumen de prueba", "puntos_clave": ["punto 1"]}'
        )


class DummyChats:
    def create(self, model: str):
        assert model == "gemini-3.6-flash"
        return DummyChat()


class DummyClient:
    chats = DummyChats()


def test_llamar_llm_estructurado_parsa_json_cuando_parsed_es_none(monkeypatch):
    monkeypatch.setattr("app.services.llm_service.get_gemini_client", lambda: DummyClient())

    resultado = llamar_llm_estructurado("prompt de prueba", ResumenOutput)

    assert resultado.resumen == "Resumen de prueba"
    assert resultado.puntos_clave == ["punto 1"]
