"""Tests de los usos de **kwargs:
- Herencia con kwargs en los procedimientos (valores por defecto y propios).
- Datos de diagnóstico (**detalles) en CalidadError.
El filtrado de Empresa con **filtros se prueba en test_empresa.py.
"""
import pytest

from classes.lote import Lote
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.excepciones import CalidadError, TransicionIlegalError


class TestProcedimientoKwargs:
    def test_proc_dimensional_valores_por_defecto_y_propios(self):
        # Valores por defecto: categoria_equipo_requerida="Dimensional" y unidad_medida="mm"
        proc = ProcedimientoDimensional(limite_gravedad_acumulada=8)
        assert proc.categoria_equipo_requerida == "Dimensional"
        assert proc.unidad_medida == "mm"
        assert proc.limite_gravedad_acumulada == 8

        # Valores propios pasados por kwargs
        proc2 = ProcedimientoDimensional(
            limite_gravedad_acumulada=12,
            unidad_medida="micras",
            categoria_equipo_requerida="Micrometro",
            certificacion_requerida="ISODIM"
        )
        assert proc2.unidad_medida == "micras"
        assert proc2.categoria_equipo_requerida == "Micrometro"
        assert proc2.certificacion_requerida == "ISODIM"

    def test_proc_visual_valores_por_defecto_y_propios(self):
        proc = ProcedimientoVisual(limite_gravedad_acumulada=5)
        assert proc.categoria_equipo_requerida == "Visual"
        assert proc.certificacion_requerida is None

        proc2 = ProcedimientoVisual(
            limite_gravedad_acumulada=6,
            certificacion_requerida="ISOVIS"
        )
        assert proc2.categoria_equipo_requerida == "Visual"
        assert proc2.certificacion_requerida == "ISOVIS"


class TestExcepcionesContextoKwargs:
    def test_calidad_error_detalles_vacio_por_defecto(self):
        err = CalidadError("Error simple")
        assert err.detalles == {}

    def test_calidad_error_con_detalles_kwargs(self):
        err = TransicionIlegalError(
            "Capacidad excedida",
            lote_id="LOT-001",
            capacidad_max=1000,
            solicitado=200
        )
        assert err.detalles["lote_id"] == "LOT-001"
        assert err.detalles["capacidad_max"] == 1000
        assert err.detalles["solicitado"] == 200

    def test_lote_crear_muestra_exceso_adjunta_detalles(self):
        lote = Lote("Pernos", 100)
        with pytest.raises(TransicionIlegalError) as exc_info:
            lote.crear_muestra(150)
        e = exc_info.value
        assert "lote_id" in e.detalles
        assert e.detalles["capacidad_usada"] == 0
        assert e.detalles["cantidad_solicitada"] == 150
        assert e.detalles["cantidad_fabricada"] == 100
