"""Tests de Profesional: ajout certification, vérification vigente, dict usage."""
import pytest
from datetime import date

from classes.profesional import Profesional
from classes.certificacion import Certificacion
from classes.excepciones import DatosInvalidosError


class TestCreacionProfesional:
    def test_creacion_valida(self):
        prof = Profesional("Ana")
        assert prof.nombre == "Ana"
        assert prof.certificaciones == {}

    def test_nombre_vacio_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            Profesional("")


class TestCertificaciones:
    def test_agregar_certificacion(self):
        prof = Profesional("Ana")
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        prof.agregar_certificacion(cert)
        assert "ISO" in prof.certificaciones

    def test_agregar_no_certificacion_rechazado(self):
        prof = Profesional("Ana")
        with pytest.raises(DatosInvalidosError):
            prof.agregar_certificacion("ISO9001")

    def test_tiene_certificacion_vigente(self):
        prof = Profesional("Ana")
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        prof.agregar_certificacion(cert)
        assert prof.tiene_certificacion_vigente("ISO", date(2025, 6, 15)) is True

    def test_certificacion_vigente_en_limite_inicio(self):
        prof = Profesional("Ana")
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        prof.agregar_certificacion(cert)
        assert prof.tiene_certificacion_vigente("ISO", date(2025, 1, 1)) is True

    def test_certificacion_vigente_en_limite_fin(self):
        prof = Profesional("Ana")
        cert = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        prof.agregar_certificacion(cert)
        assert prof.tiene_certificacion_vigente("ISO", date(2025, 12, 31)) is True

    def test_certificacion_vencida(self):
        prof = Profesional("Ana")
        cert = Certificacion("ISO", date(2023, 1, 1), date(2023, 12, 31))
        prof.agregar_certificacion(cert)
        assert prof.tiene_certificacion_vigente("ISO", date(2025, 6, 15)) is False

    def test_certificacion_ausente(self):
        prof = Profesional("Ana")
        assert prof.tiene_certificacion_vigente("ISO", date(2025, 6, 15)) is False

    def test_certificaciones_retorna_copia(self):
        """El dict retornado es una copia, no la referencia interna."""
        prof = Profesional("Ana")
        certs = prof.certificaciones
        certs["FAKE"] = "x"
        assert "FAKE" not in prof.certificaciones
