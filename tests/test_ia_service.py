"""Pruebas unitarias de las 4 funciones de IA (Paso 6), con el LLM
mockeado para no depender de una llamada real a Gemini."""
from app.models.email import Categoria
from app.models.schemas import BorradorOutput, ClasificacionOutput
from app.services import ia_service


def test_clasificar_email_llama_al_llm_con_el_esquema_correcto(mocker):
    mock_llamada = mocker.patch(
        "app.services.ia_service.llamar_llm_estructurado",
        return_value=ClasificacionOutput(categoria=Categoria.FACTURAS, confianza=0.8, justificacion="x"),
    )

    resultado = ia_service.clasificar_email(
        remitente="a@b.com", asunto="Factura", cuerpo="Tu factura ya está lista."
    )

    assert resultado.categoria == Categoria.FACTURAS
    mock_llamada.assert_called_once()
    _, esquema_usado = mock_llamada.call_args[0]
    assert esquema_usado is ClasificacionOutput


def test_redactar_borrador_no_llama_al_llm_para_promociones(mocker):
    mock_llamada = mocker.patch("app.services.ia_service.llamar_llm_estructurado")

    resultado = ia_service.redactar_borrador(
        remitente="ofertas@tienda.com",
        asunto="50% de descuento",
        cuerpo="Aprovecha ya.",
        categoria=Categoria.PROMOCIONES,
    )

    assert resultado == BorradorOutput(aplica=False, borrador="")
    mock_llamada.assert_not_called()


def test_redactar_borrador_si_llama_al_llm_para_trabajo(mocker):
    mocker.patch(
        "app.services.ia_service.llamar_llm_estructurado",
        return_value=BorradorOutput(aplica=True, borrador="Confirmo."),
    )

    resultado = ia_service.redactar_borrador(
        remitente="jefe@empresa.com",
        asunto="Reunión",
        cuerpo="¿Confirmas?",
        categoria=Categoria.TRABAJO,
    )

    assert resultado.aplica is True