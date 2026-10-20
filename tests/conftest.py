"""Fixtures compartidas por varios archivos de tests (pytest las inyecta por nombre)."""
import pytest
from datetime import date

from classes.muestra import Muestra
from classes.lote import Lote
from classes.profesional import Profesional
from classes.certificacion import Certificacion
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual


@pytest.fixture
def muestra():
    return Muestra(50, "L1")


@pytest.fixture
def lote():
    return Lote("Tornillos", 1000)


@pytest.fixture
def profesional():
    return Profesional("Ana")


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
