"""Pruebas de validación de los esquemas de salida del LLM (Paso 4)."""
import pytest
from pydantic import ValidationError

from app.models.schemas import BorradorOutput, ClasificacionOutput, ResumenOutput


def test_clasificacion_valida():
    obj = ClasificacionOutput(categoria="trabajo", confianza=0.92, justificacion="Menciona una reunión.")
    assert obj.categoria == "trabajo"
    assert 0 <= obj.confianza <= 1


def test_clasificacion_rechaza_categoria_inexistente():
    with pytest.raises(ValidationError):
        ClasificacionOutput(categoria="deportes", confianza=0.5, justificacion="x")


def test_clasificacion_rechaza_confianza_fuera_de_rango():
    with pytest.raises(ValidationError):
        ClasificacionOutput(categoria="trabajo", confianza=1.5, justificacion="x")


def test_borrador_output_vacio_por_defecto():
    obj = BorradorOutput(aplica=False)
    assert obj.borrador == ""


def test_resumen_output_puntos_clave_por_defecto_vacios():
    obj = ResumenOutput(resumen="Un resumen breve.")
    assert obj.puntos_clave == []