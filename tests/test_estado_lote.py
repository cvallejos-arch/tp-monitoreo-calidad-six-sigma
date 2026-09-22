"""Tests des enums EstadoLote et EstadoMuestra."""
import pytest

from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra


class TestEstadoLote:
    def test_valores(self):
        assert EstadoLote.EN_PRODUCCION.value == "EN_PRODUCCION"
        assert EstadoLote.APROBADO.value == "APROBADO"
        assert EstadoLote.RECHAZADO.value == "RECHAZADO"

    def test_cantidad_estados(self):
        assert len(EstadoLote) == 3


class TestEstadoMuestra:
    def test_valores(self):
        assert EstadoMuestra.PENDIENTE.value == "PENDIENTE"
        assert EstadoMuestra.EN_INSPECCION.value == "EN_INSPECCION"
        assert EstadoMuestra.CONFORME.value == "CONFORME"
        assert EstadoMuestra.NO_CONFORME.value == "NO_CONFORME"

    def test_cantidad_estados(self):
        assert len(EstadoMuestra) == 4
