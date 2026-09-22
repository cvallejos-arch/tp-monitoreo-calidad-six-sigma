"""Fixtures compartidas para todos los tests."""
import pytest
from datetime import date, timedelta

from classes.defecto import Defecto
from classes.muestra import Muestra
from classes.lote import Lote
from classes.equipo import Equipo
from classes.profesional import Profesional
from classes.certificacion import Certificacion
from classes.procedimiento import Procedimiento
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.observacion_visual import ObservacionVisual
from classes.inspeccion import Inspeccion


# --- Fechas de referencia ---
FECHA_HOY = date(2025, 6, 15)
FECHA_CALIBRACION_VALIDA = FECHA_HOY - timedelta(days=100)
FECHA_CALIBRACION_EXACTA_182 = FECHA_HOY - timedelta(days=182)
FECHA_CALIBRACION_VENCIDA = FECHA_HOY - timedelta(days=183)


@pytest.fixture
def defecto_leve():
    return Defecto("VISUAL", "Rayadura superficial", 1)


@pytest.fixture
def defecto_medio():
    return Defecto("DIMENSIONAL", "Desviación leve", 3)


@pytest.fixture
def defecto_critico():
    return Defecto("VISUAL", "Fractura completa", 5)


@pytest.fixture
def muestra():
    return Muestra(50)


@pytest.fixture
def lote():
    return Lote("Tornillos", 1000)


@pytest.fixture
def equipo_dimensional():
    return Equipo("Dimensional", FECHA_CALIBRACION_VALIDA)


@pytest.fixture
def equipo_visual():
    return Equipo("Visual", FECHA_CALIBRACION_VALIDA)


@pytest.fixture
def profesional():
    return Profesional("Ana")


@pytest.fixture
def cert_vigente():
    return Certificacion(
        "ISO",
        date(2025, 1, 1),
        date(2025, 12, 31)
    )


@pytest.fixture
def cert_vencida():
    return Certificacion(
        "ISO",
        date(2023, 1, 1),
        date(2023, 12, 31)
    )


@pytest.fixture
def proc_dimensional():
    return ProcedimientoDimensional(
        limite_gravedad_acumulada=5,
        categoria_equipo_requerida="Dimensional"
    )


@pytest.fixture
def proc_visual():
    return ProcedimientoVisual(
        limite_gravedad_acumulada=5,
        categoria_equipo_requerida="Visual"
    )


@pytest.fixture
def proc_con_cert():
    return ProcedimientoVisual(
        limite_gravedad_acumulada=5,
        categoria_equipo_requerida="Visual",
        certificacion_requerida="ISO"
    )
