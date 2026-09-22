"""Tests d'Inspeccion: flux complet, certification, calibration, catégorie incompatible."""
import pytest
from datetime import date, timedelta

from classes.inspeccion import Inspeccion
from classes.muestra import Muestra
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import (
    CertificacionNoVigenteError,
    EquipoNoAptoError,
    TransicionIlegalError,
    InspeccionInvalidaError,
    DatosInvalidosError,
)

FECHA = date(2025, 6, 15)


def _setup_basico(categoria="Visual", con_cert=False, cert_nombre=None):
    """Helper pour créer les objets de base d'une inspection."""
    muestra = Muestra(50)
    muestra.asignar_lote("L1")
    profesional = Profesional("Ana")
    equipo = Equipo(categoria, FECHA - timedelta(days=100))

    cert_req = None
    if con_cert:
        cert_req = cert_nombre or "ISO"
        cert = Certificacion(cert_req, date(2025, 1, 1), date(2025, 12, 31))
        profesional.agregar_certificacion(cert)

    if cert_req:
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida=categoria,
            certificacion_requerida=cert_req
        )
    else:
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida=categoria
        )

    return muestra, profesional, equipo, proc


class TestCreacionInspeccion:
    def test_creacion_valida(self):
        muestra, prof, equipo, proc = _setup_basico()
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        assert insp.muestra_id == muestra.id
        assert insp.profesional_id == prof.id
        assert insp.equipo_id == equipo.id
        assert insp.fecha == FECHA
        assert muestra.estado == EstadoMuestra.EN_INSPECCION

    def test_muestra_no_pendiente_rechazada(self):
        muestra, prof, equipo, proc = _setup_basico()
        muestra.iniciar_inspeccion()  # ya no está pendiente
        with pytest.raises(TransicionIlegalError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)

    def test_fecha_invalida_rechazada(self):
        muestra, prof, equipo, proc = _setup_basico()
        with pytest.raises(DatosInvalidosError):
            Inspeccion(muestra, prof, equipo, proc, "2025-06-15")


class TestCertificacion:
    def test_certificacion_ausente_rechazada(self):
        """Profesional sin ninguna certificación cuando el procedimiento la requiere."""
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")  # sin certificaciones
        equipo = Equipo("Visual", FECHA - timedelta(days=100))
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual",
            certificacion_requerida="ISO"
        )
        with pytest.raises(CertificacionNoVigenteError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)

    def test_certificacion_vencida_rechazada(self):
        """Certificación existente pero vencida."""
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")
        cert_vencida = Certificacion("ISO", date(2023, 1, 1), date(2023, 12, 31))
        prof.agregar_certificacion(cert_vencida)
        equipo = Equipo("Visual", FECHA - timedelta(days=100))
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual",
            certificacion_requerida="ISO"
        )
        with pytest.raises(CertificacionNoVigenteError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)

    def test_certificacion_vigente_aceptada(self):
        muestra, prof, equipo, proc = _setup_basico(con_cert=True)
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        assert insp is not None

    def test_sin_certificacion_requerida_ok(self):
        """Procedimiento sin certificación requerida → acepta cualquier profesional."""
        muestra, prof, equipo, proc = _setup_basico()
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        assert insp is not None

    def test_inspeccion_rechazada_no_modifica_muestra(self):
        """Si se rechaza por certificación, la muestra queda PENDIENTE."""
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")  # sin cert
        equipo = Equipo("Visual", FECHA - timedelta(days=100))
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual",
            certificacion_requerida="ISO"
        )
        with pytest.raises(CertificacionNoVigenteError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)
        assert muestra.estado == EstadoMuestra.PENDIENTE


class TestEquipoValidacion:
    def test_equipo_categoria_incompatible(self):
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")
        equipo = Equipo("Dimensional", FECHA - timedelta(days=100))  # Dimensional ≠ Visual
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        with pytest.raises(EquipoNoAptoError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)

    def test_equipo_calibracion_vencida(self):
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")
        equipo = Equipo("Visual", FECHA - timedelta(days=183))  # 183 jours = vencido
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        with pytest.raises(EquipoNoAptoError):
            Inspeccion(muestra, prof, equipo, proc, FECHA)

    def test_equipo_calibracion_exacta_182_dias(self):
        """182 días exactos = calibrado (borne inclusive)."""
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")
        equipo = Equipo("Visual", FECHA - timedelta(days=182))
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        assert insp is not None


class TestEjecucionInspeccion:
    def test_ejecutar_y_cerrar_visual(self):
        muestra, prof, equipo, proc = _setup_basico()
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)

        obs = [
            ObservacionVisual("Sin defecto", False),
            ObservacionVisual("Rayadura visible", True, 3),
        ]
        defectos = insp.ejecutar(obs)
        assert len(defectos) == 1
        assert defectos[0].gravedad == 3

        insp.cerrar()
        assert muestra.estado == EstadoMuestra.CONFORME  # 3 <= 5

    def test_ejecutar_inspeccion_cerrada_rechazada(self):
        muestra, prof, equipo, proc = _setup_basico()
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        insp.ejecutar([])
        insp.cerrar()
        with pytest.raises(InspeccionInvalidaError):
            insp.ejecutar([])

    def test_cerrar_inspeccion_dos_veces_rechazada(self):
        muestra, prof, equipo, proc = _setup_basico()
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)
        insp.cerrar()
        with pytest.raises(InspeccionInvalidaError):
            insp.cerrar()

    def test_ejecutar_dimensional(self):
        muestra = Muestra(50)
        muestra.asignar_lote("L1")
        prof = Profesional("Ana")
        equipo = Equipo("Dimensional", FECHA - timedelta(days=100))
        proc = ProcedimientoDimensional(
            limite_gravedad_acumulada=10,
            categoria_equipo_requerida="Dimensional"
        )
        insp = Inspeccion(muestra, prof, equipo, proc, FECHA)

        obs = [
            ObservacionDimensional(10.5, 9.0, 10.0, "Pieza fuera de rango"),
            ObservacionDimensional(9.5, 9.0, 10.0, "Pieza dentro de rango"),
        ]
        defectos = insp.ejecutar(obs)
        assert len(defectos) == 1  # solo la primera tiene desviación > 0
