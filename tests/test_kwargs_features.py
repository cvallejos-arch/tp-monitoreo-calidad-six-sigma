"""Tests unitaires pour les fonctionnalités avancées utilisant **kwargs :
- Héritage coopératif avec kwargs dans Procedimiento
- Métadonnées contextuelles de diagnostic dans CalidadError
- Filtrage dynamique dans Empresa (listar_lotes, listar_inspecciones, listar_muestras)
"""
import pytest
from datetime import date

from classes.empresa import Empresa
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.excepciones import (
    CalidadError,
    TransicionIlegalError,
    EquipoNoAptoError,
    CertificacionNoVigenteError,
)
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.certificacion import Certificacion


class TestProcedimientoKwargs:
    def test_proc_dimensional_defaults_and_custom_kwargs(self):
        # Default categoria_equipo_requerida="Dimensional" and default unidad_medida="mm"
        proc = ProcedimientoDimensional(limite_gravedad_acumulada=8)
        assert proc.categoria_equipo_requerida == "Dimensional"
        assert proc.unidad_medida == "mm"
        assert proc.limite_gravedad_acumulada == 8

        # Custom kwargs
        proc2 = ProcedimientoDimensional(
            limite_gravedad_acumulada=12,
            unidad_medida="micras",
            categoria_equipo_requerida="Micrometro",
            certificacion_requerida="ISODIM"
        )
        assert proc2.unidad_medida == "micras"
        assert proc2.categoria_equipo_requerida == "Micrometro"
        assert proc2.certificacion_requerida == "ISODIM"

    def test_proc_visual_defaults_and_custom_kwargs(self):
        proc = ProcedimientoVisual(limite_gravedad_acumulada=5)
        assert proc.categoria_equipo_requerida == "Visual"
        assert proc.nivel_iluminacion_minimo is None

        proc2 = ProcedimientoVisual(
            limite_gravedad_acumulada=6,
            nivel_iluminacion_minimo=500,
            certificacion_requerida="ISOVIS"
        )
        assert proc2.categoria_equipo_requerida == "Visual"
        assert proc2.nivel_iluminacion_minimo == 500
        assert proc2.certificacion_requerida == "ISOVIS"


class TestExcepcionesContextoKwargs:
    def test_calidad_error_detalles_vacio_por_defecto(self):
        err = CalidadError("Erreur simple")
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
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Pernos", 100)
        with pytest.raises(TransicionIlegalError) as exc_info:
            lote.crear_muestra(150)
        e = exc_info.value
        assert "lote_id" in e.detalles
        assert e.detalles["capacidad_usada"] == 0
        assert e.detalles["cantidad_solicitada"] == 150
        assert e.detalles["cantidad_fabricada"] == 100


class TestEmpresaFiltradoDinamicoKwargs:
    def test_filtrar_lotes(self):
        empresa = Empresa()
        lote1 = empresa.crear_registrar_lote("Tornillos", 100)
        lote2 = empresa.crear_registrar_lote("Tuercas", 200)

        # Sin filtros
        assert len(empresa.listar_lotes()) == 2

        # Filtro por nombre_componentes
        res = empresa.listar_lotes(nombre_componentes="Tornillos")
        assert len(res) == 1
        assert res[0].id == lote1.id

        # Filtro por estado
        assert len(empresa.listar_lotes(estado=EstadoLote.EN_PRODUCCION)) == 2
        assert len(empresa.listar_lotes(estado=EstadoLote.APROBADO)) == 0

    def test_filtrar_muestras_e_inspecciones(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Arandelas", 500)
        m1 = empresa.crear_registrar_muestra(50, lote)
        m2 = empresa.crear_registrar_muestra(50, lote)

        # Filtro de muestras por estado
        assert len(empresa.listar_muestras(estado=EstadoMuestra.PENDIENTE)) == 2
        assert len(empresa.listar_muestras(estado=EstadoMuestra.CONFORME)) == 0

        # Crear inspección y verificar filtro de inspecciones
        prof = empresa.crear_registrar_profesional("Laura")
        prof.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
        equipo = empresa.crear_registrar_equipo("Visual", date(2025, 5, 1))
        proc = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)
        insp = empresa.lanzar_inspeccion(m1, prof, equipo, proc, date(2025, 6, 1))

        assert len(empresa.listar_inspecciones(cerrada=False)) == 1
        assert len(empresa.listar_inspecciones(cerrada=True)) == 0

        insp.cerrar()
        assert len(empresa.listar_inspecciones(cerrada=True)) == 1
        assert len(empresa.listar_inspecciones(cerrada=False)) == 0
