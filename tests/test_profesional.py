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



class TestCertificacionesVigentes:
    def test_sin_certificaciones_retorna_tupla_vacia(self):
        prof = Profesional("Ana")
        assert prof.certificaciones_vigentes(date(2025, 6, 15)) == ()

    def test_filtra_solo_las_vigentes(self):
        prof = Profesional("Ana")
        vigente = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        vencida = Certificacion("Seguridad", date(2023, 1, 1), date(2023, 12, 31))
        prof.agregar_certificacion(vigente)
        prof.agregar_certificacion(vencida)

        resultado = prof.certificaciones_vigentes(date(2025, 6, 15))

        assert resultado == (vigente,)

    def test_ninguna_vigente_en_la_fecha(self):
        prof = Profesional("Ana")
        prof.agregar_certificacion(
            Certificacion("ISO", date(2023, 1, 1), date(2023, 12, 31))
        )
        assert prof.certificaciones_vigentes(date(2025, 6, 15)) == ()

    def test_retorna_tupla(self):
        """Devuelve una tupla para que no se pueda modificar desde afuera."""
        prof = Profesional("Ana")
        assert isinstance(prof.certificaciones_vigentes(date(2025, 6, 15)), tuple)


class TestReprProfesional:
    def test_repr_incluye_nombre_y_certificaciones(self):
        prof = Profesional("Ana")
        prof.agregar_certificacion(
            Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        )
        texto = repr(prof)
        assert "Ana" in texto
        assert "ISO" in texto

    def test_repr_sin_certificaciones(self):
        prof = Profesional("Ana")
        assert "Ana" in repr(prof)
