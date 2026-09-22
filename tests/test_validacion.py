"""Tests de validación: todas las funciones del módulo validacion.py."""
import pytest
from datetime import date

from classes.validacion import (
    validar_entero, validar_cantidad, validar_gravedad,
    validar_texto, validar_descripcion, validar_rango_fechas,
    validar_fecha_tipo, validar_rango_entero
)
from classes.excepciones import DatosInvalidosError


# --- validar_entero ---

class TestValidarEntero:
    def test_entero_valido(self):
        assert validar_entero(5) == 5

    def test_entero_cero(self):
        assert validar_entero(0) == 0

    def test_entero_negativo(self):
        assert validar_entero(-3) == -3

    def test_string_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_entero("5")

    def test_float_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_entero(5.0)

    def test_bool_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_entero(True)

    def test_none_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_entero(None)


# --- validar_cantidad ---

class TestValidarCantidad:
    def test_cantidad_positiva(self):
        assert validar_cantidad(10) == 10

    def test_cantidad_uno(self):
        assert validar_cantidad(1) == 1

    def test_cantidad_cero_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_cantidad(0)

    def test_cantidad_negativa_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_cantidad(-1)

    def test_cantidad_string_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_cantidad("10")


# --- validar_gravedad ---

class TestValidarGravedad:
    def test_gravedad_uno(self):
        assert validar_gravedad(1) == 1

    def test_gravedad_cinco(self):
        assert validar_gravedad(5) == 5

    def test_gravedad_tres(self):
        assert validar_gravedad(3) == 3

    def test_gravedad_cero_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_gravedad(0)

    def test_gravedad_seis_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_gravedad(6)

    def test_gravedad_negativa_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_gravedad(-1)


# --- validar_texto ---

class TestValidarTexto:
    def test_texto_valido(self):
        assert validar_texto("Dimensional") == "Dimensional"

    def test_texto_con_espacios(self):
        assert validar_texto("Control Visual") == "Control Visual"

    def test_texto_vacio_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_texto("")

    def test_texto_solo_espacios_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_texto("   ")

    def test_texto_numeros_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_texto("ISO9001")

    def test_texto_none_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_texto(None)


# --- validar_descripcion ---

class TestValidarDescripcion:
    def test_descripcion_valida(self):
        assert validar_descripcion("Rayadura superficial") == "Rayadura superficial"

    def test_descripcion_con_numeros(self):
        assert validar_descripcion("Desviación de 0.5mm") == "Desviación de 0.5mm"

    def test_descripcion_vacia_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            validar_descripcion("")


# --- validar_rango_fechas ---

class TestValidarRangoFechas:
    def test_rango_valido(self):
        validar_rango_fechas(date(2025, 1, 1), date(2025, 12, 31))

    def test_misma_fecha(self):
        validar_rango_fechas(date(2025, 6, 15), date(2025, 6, 15))

    def test_rango_invertido_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_rango_fechas(date(2025, 12, 31), date(2025, 1, 1))


# --- validar_fecha_tipo ---

class TestValidarFechaTipo:
    def test_date_valido(self):
        f = date(2025, 6, 15)
        assert validar_fecha_tipo(f) == f

    def test_string_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_fecha_tipo("2025-06-15")

    def test_none_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            validar_fecha_tipo(None)


# --- validar_rango_entero ---

class TestValidarRangoEntero:
    def test_dentro_de_rango(self):
        assert validar_rango_entero(3, 1, 5, "test") == 3

    def test_en_limite_inferior(self):
        assert validar_rango_entero(1, 1, 5, "test") == 1

    def test_en_limite_superior(self):
        assert validar_rango_entero(5, 1, 5, "test") == 5

    def test_fuera_por_arriba(self):
        with pytest.raises(DatosInvalidosError):
            validar_rango_entero(6, 1, 5, "test")

    def test_fuera_por_abajo(self):
        with pytest.raises(DatosInvalidosError):
            validar_rango_entero(0, 1, 5, "test")
