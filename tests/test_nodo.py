"""Tests de Nodo: creación, enlace con el siguiente y validación de tipo del dato."""
import pytest

from classes.nodo import Nodo
from classes.excepciones import DatosInvalidosError


class TestCreacionNodo:
    def test_creacion_guarda_dato(self):
        nodo = Nodo(5)
        assert nodo.get_dato() == 5

    def test_siguiente_inicial_es_none(self):
        nodo = Nodo(5)
        assert nodo.get_siguiente() is None

    def test_str_muestra_el_dato(self):
        assert str(Nodo(5)) == "5"

    def test_repr_muestra_el_dato(self):
        assert repr(Nodo("a")) == "Nodo(dato='a')"


class TestSetDato:
    def test_set_dato_mismo_tipo(self):
        nodo = Nodo(5)
        nodo.set_dato(10)
        assert nodo.get_dato() == 10

    def test_set_dato_otro_tipo_rechazado(self):
        nodo = Nodo(5)
        with pytest.raises(DatosInvalidosError):
            nodo.set_dato("cinco")

    def test_set_dato_rechazado_no_modifica(self):
        nodo = Nodo(5)
        with pytest.raises(DatosInvalidosError):
            nodo.set_dato(5.0)
        assert nodo.get_dato() == 5


class TestSetSiguiente:
    def test_enlazar_dos_nodos(self):
        primero = Nodo(1)
        segundo = Nodo(2)
        primero.set_siguiente(segundo)
        assert primero.get_siguiente() is segundo

    def test_set_siguiente_none_corta_el_enlace(self):
        primero = Nodo(1)
        primero.set_siguiente(Nodo(2))
        primero.set_siguiente(None)
        assert primero.get_siguiente() is None

    def test_set_siguiente_no_nodo_rechazado(self):
        nodo = Nodo(1)
        with pytest.raises(DatosInvalidosError):
            nodo.set_siguiente(2)
