"""Tests de Defecto: creación, gravedad 1-5, hors range, defecto critico."""
import pytest

from classes.defecto import Defecto
from classes.excepciones import DatosInvalidosError


class TestCreacionDefecto:
    def test_creacion_valida(self):
        d = Defecto("VISUAL", "Rayadura superficial", 3)
        assert d.tipo == "VISUAL"
        assert d.descripcion == "Rayadura superficial"
        assert d.gravedad == 3

    def test_gravedad_uno(self):
        d = Defecto("VISUAL", "Marca leve", 1)
        assert d.gravedad == 1
        assert not d.es_critico()

    def test_gravedad_cinco_es_critico(self):
        d = Defecto("VISUAL", "Fractura completa", 5)
        assert d.gravedad == 5
        assert d.es_critico()

    def test_gravedad_cero_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Defecto("VISUAL", "Test", 0)

    def test_gravedad_seis_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Defecto("VISUAL", "Test", 6)

    def test_gravedad_negativa_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Defecto("VISUAL", "Test", -1)

    def test_tipo_vacio_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            Defecto("", "Descripción", 3)

    def test_descripcion_vacia_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Defecto("VISUAL", "", 3)


class TestCopiaDefecto:
    def test_copia_es_independiente(self):
        original = Defecto("VISUAL", "Rayadura", 3)
        copia = original.copia()
        assert copia.tipo == original.tipo
        assert copia.descripcion == original.descripcion
        assert copia.gravedad == original.gravedad
        assert copia is not original
