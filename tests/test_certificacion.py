"""Tests de Certificacion: vigencia en bornes inclusivos."""
import pytest
from datetime import date

from classes.certificacion import Certificacion
from classes.excepciones import DatosInvalidosError


class TestCreacionCertificacion:
    def test_creacion_valida(self):
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.nombre == "ISO"
        assert cert.fecha_inicio == date(2025, 1, 1)
        assert cert.fecha_fin == date(2025, 12, 31)

    def test_nombre_vacio_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            Certificacion("", date(2025, 1, 1), date(2025, 12, 31))

    def test_rango_invertido_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            Certificacion("ISO", date(2025, 12, 31), date(2025, 1, 1))


class TestVigenciaCertificacion:
    def test_vigente_en_fecha_inicio(self):
        """Borne inclusivo inferior."""
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.es_vigente(date(2025, 1, 1)) is True

    def test_vigente_en_fecha_fin(self):
        """Borne inclusivo superior."""
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.es_vigente(date(2025, 12, 31)) is True

    def test_vigente_en_medio(self):
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.es_vigente(date(2025, 6, 15)) is True

    def test_no_vigente_antes(self):
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.es_vigente(date(2024, 12, 31)) is False

    def test_no_vigente_despues(self):
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        assert cert.es_vigente(date(2026, 1, 1)) is False

    def test_vigente_un_solo_dia(self):
        cert = Certificacion("ISO", date(2025, 6, 15), date(2025, 6, 15))
        assert cert.es_vigente(date(2025, 6, 15)) is True
        assert cert.es_vigente(date(2025, 6, 14)) is False
        assert cert.es_vigente(date(2025, 6, 16)) is False
