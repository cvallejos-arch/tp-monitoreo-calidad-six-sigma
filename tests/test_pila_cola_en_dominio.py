"""Tests del uso de Pila y Cola dentro del sistema:
- Muestra guarda su historial de estados en una Pila.
- Lote mantiene una Cola de muestras pendientes en orden de creación.
- Empresa lanza la inspección de la siguiente muestra pendiente."""
import pytest
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.lote import Lote
from classes.muestra import Muestra
from classes.defecto import Defecto
from classes.reporte import Reporte
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import EstructuraVaciaError

FECHA = date(2025, 6, 15)


def _inspeccion_falsa():
    """Objeto mínimo con los datos que Muestra.cerrar() lee de la inspección."""
    return type('obj', (object,), {'profesional_id': 'p1', 'fecha': FECHA})()


class TestHistorialMuestra:
    def test_historial_inicial_es_pendiente(self):
        muestra = Muestra(10, "L1")
        assert muestra.historial_estados == (EstadoMuestra.PENDIENTE,)
        assert muestra.estado == EstadoMuestra.PENDIENTE

    def test_historial_registra_cada_transicion(self):
        muestra = Muestra(10, "L1")
        muestra.iniciar_inspeccion()
        muestra._inspeccion = _inspeccion_falsa()
        muestra.cerrar(10)
        assert muestra.historial_estados == (
            EstadoMuestra.PENDIENTE,
            EstadoMuestra.EN_INSPECCION,
            EstadoMuestra.CONFORME,
        )

    def test_estado_es_el_tope_del_historial(self):
        muestra = Muestra(10, "L1")
        muestra.iniciar_inspeccion()
        assert muestra.estado == muestra.historial_estados[-1]

    def test_reporte_guarda_historial(self):
        muestra = Muestra(10, "L1")
        muestra.iniciar_inspeccion()
        muestra._inspeccion = _inspeccion_falsa()
        muestra.agregar_defecto(Defecto("VISUAL", "Fractura", 5))
        muestra.cerrar(10)
        assert muestra.reporte.historial_estados == (
            EstadoMuestra.PENDIENTE,
            EstadoMuestra.EN_INSPECCION,
            EstadoMuestra.NO_CONFORME,
        )


class TestReporteHistorial:
    def test_historial_por_defecto_vacio(self):
        reporte = Reporte("M1", "L1", "P1", FECHA, [])
        assert reporte.historial_estados == ()

    def test_historial_es_copia_inmutable(self):
        estados = [EstadoMuestra.PENDIENTE]
        reporte = Reporte("M1", "L1", "P1", FECHA, [], historial_estados=estados)
        estados.append(EstadoMuestra.CONFORME)
        assert reporte.historial_estados == (EstadoMuestra.PENDIENTE,)


class TestColaPendientesLote:
    def test_lote_sin_muestras_no_tiene_pendiente(self):
        assert Lote("Tornillos", 100).siguiente_muestra_pendiente() is None

    def test_siguiente_pendiente_respeta_orden_de_creacion(self):
        lote = Lote("Tornillos", 100)
        primera = lote.crear_muestra(10)
        lote.crear_muestra(10)
        assert lote.siguiente_muestra_pendiente() is primera

    def test_siguiente_pendiente_no_desencola(self):
        lote = Lote("Tornillos", 100)
        primera = lote.crear_muestra(10)
        lote.siguiente_muestra_pendiente()
        assert lote.siguiente_muestra_pendiente() is primera

    def test_salta_las_que_ya_no_estan_pendientes(self):
        lote = Lote("Tornillos", 100)
        primera = lote.crear_muestra(10)
        segunda = lote.crear_muestra(10)
        primera.iniciar_inspeccion()
        assert lote.siguiente_muestra_pendiente() is segunda

    def test_pendientes_en_orden(self):
        lote = Lote("Tornillos", 100)
        m1 = lote.crear_muestra(10)
        m2 = lote.crear_muestra(10)
        m3 = lote.crear_muestra(10)
        m2.iniciar_inspeccion()
        assert lote.pendientes_en_orden() == (m1, m3)


class TestLanzarSiguienteInspeccion:
    @pytest.fixture
    def contexto(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        profesional = empresa.crear_registrar_profesional("Ana")
        profesional.agregar_certificacion(
            Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
        )
        equipo = empresa.crear_registrar_equipo("Visual", FECHA - timedelta(days=10))
        procedimiento = empresa.crear_registrar_procedimiento(
            ProcedimientoVisual, limite_gravedad_acumulada=5
        )
        return empresa, lote, profesional, equipo, procedimiento

    def test_inspecciona_las_muestras_en_orden(self, contexto):
        empresa, lote, profesional, equipo, procedimiento = contexto
        m1 = empresa.crear_registrar_muestra(10, lote)
        m2 = empresa.crear_registrar_muestra(10, lote)

        insp_1 = empresa.lanzar_siguiente_inspeccion(lote, profesional, equipo, procedimiento, FECHA)
        insp_2 = empresa.lanzar_siguiente_inspeccion(lote, profesional, equipo, procedimiento, FECHA)

        assert insp_1.muestra_id == m1.id
        assert insp_2.muestra_id == m2.id

    def test_sin_pendientes_lanza_error(self, contexto):
        empresa, lote, profesional, equipo, procedimiento = contexto
        with pytest.raises(EstructuraVaciaError):
            empresa.lanzar_siguiente_inspeccion(lote, profesional, equipo, procedimiento, FECHA)
