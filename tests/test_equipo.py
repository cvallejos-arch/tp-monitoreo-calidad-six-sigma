"""Tests de Equipo: calibración aux bornes (182j exacte, 183j vencida), compatibilité."""
import pytest
from datetime import date, timedelta

from classes.equipo import Equipo
from classes.excepciones import DatosInvalidosError


class TestCreacionEquipo:
    def test_creacion_valida(self):
        equipo = Equipo("Dimensional", date(2025, 1, 1))
        assert equipo.categoria == "Dimensional"
        assert equipo.fecha_calibracion == date(2025, 1, 1)

    def test_categoria_vacia_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Equipo("", date(2025, 1, 1))

    def test_fecha_string_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Equipo("Dimensional", "2025-01-01")


class TestCalibracion:
    def test_calibrado_mismo_dia(self):
        """Calibración el mismo día = 0 días de diferencia."""
        fecha = date(2025, 6, 15)
        equipo = Equipo("Dimensional", fecha)
        assert equipo.esta_calibrado(fecha) is True

    def test_calibrado_exactamente_182_dias(self):
        """Exactement à 182 jours = calibrado (borne inclusive)."""
        fecha_inspeccion = date(2025, 6, 15)
        fecha_calibracion = fecha_inspeccion - timedelta(days=182)
        equipo = Equipo("Dimensional", fecha_calibracion)
        assert equipo.esta_calibrado(fecha_inspeccion) is True

    def test_vencido_183_dias(self):
        """Un jour de plus (183 dias) = vencido."""
        fecha_inspeccion = date(2025, 6, 15)
        fecha_calibracion = fecha_inspeccion - timedelta(days=183)
        equipo = Equipo("Dimensional", fecha_calibracion)
        assert equipo.esta_calibrado(fecha_inspeccion) is False

    def test_calibracion_futura_rechazada(self):
        """Calibración posterior a la fecha de inspección."""
        fecha_inspeccion = date(2025, 6, 15)
        fecha_calibracion = date(2025, 6, 16)
        equipo = Equipo("Dimensional", fecha_calibracion)
        assert equipo.esta_calibrado(fecha_inspeccion) is False

    def test_calibrado_a_100_dias(self):
        fecha_inspeccion = date(2025, 6, 15)
        fecha_calibracion = fecha_inspeccion - timedelta(days=100)
        equipo = Equipo("Dimensional", fecha_calibracion)
        assert equipo.esta_calibrado(fecha_inspeccion) is True


class TestCompatibilidad:
    def test_compatible(self):
        equipo = Equipo("Dimensional", date(2025, 1, 1))
        assert equipo.es_compatible("Dimensional") is True

    def test_incompatible(self):
        equipo = Equipo("Visual", date(2025, 1, 1))
        assert equipo.es_compatible("Dimensional") is False
