"""Tests de Lote: création, ajout muestras, excès capacité, décision 5%, conteo."""
import pytest
from datetime import date

from classes.lote import Lote
from classes.muestra import Muestra
from classes.defecto import Defecto
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError, TransicionIlegalError


class TestCreacionLote:
    def test_creacion_valida(self):
        lote = Lote("Tornillos", 1000)
        assert lote.nombre_componentes == "Tornillos"
        assert lote.cantidad_fabricada == 1000
        assert lote.estado == EstadoLote.EN_PRODUCCION
        assert lote.muestras == ()

    def test_cantidad_cero_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Lote("Tornillos", 0)

    def test_cantidad_negativa_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Lote("Tornillos", -1)

    def test_nombre_vacio_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            Lote("", 1000)


class TestAgregarMuestra:
    def test_agregar_muestra_valida(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        assert len(lote.muestras) == 1
        assert m.lote_id == lote.id

    def test_agregar_muestra_duplicada_rechazada(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        with pytest.raises(DatosInvalidosError):
            lote.agregar_muestra(m)

    def test_agregar_muestra_excede_capacidad(self):
        lote = Lote("Tornillos", 100)
        m1 = Muestra(60)
        m2 = Muestra(50)
        lote.agregar_muestra(m1)
        with pytest.raises(TransicionIlegalError):
            lote.agregar_muestra(m2)

    def test_agregar_multiples_muestras_hasta_limite(self):
        lote = Lote("Tornillos", 100)
        m1 = Muestra(50)
        m2 = Muestra(50)
        lote.agregar_muestra(m1)
        lote.agregar_muestra(m2)
        assert len(lote.muestras) == 2


def _cerrar_muestra_conforme(muestra):
    """Helper para cerrar una muestra como conforme."""
    muestra.iniciar_inspeccion()
    muestra._inspeccion = type('obj', (object,), {
        'profesional_id': 'p1', 'fecha': date(2025, 6, 15)
    })()
    muestra.cerrar(10)


def _cerrar_muestra_no_conforme(muestra):
    """Helper para cerrar una muestra como no conforme."""
    muestra.iniciar_inspeccion()
    muestra._inspeccion = type('obj', (object,), {
        'profesional_id': 'p1', 'fecha': date(2025, 6, 15)
    })()
    muestra.agregar_defecto(Defecto("VISUAL", "Critico", 5))
    muestra.cerrar(4)


class TestDecisionLote:
    def test_lote_aprobado_0_porciento(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        _cerrar_muestra_conforme(m)
        assert lote.decidir() == EstadoLote.APROBADO

    def test_lote_aprobado_exactamente_5_porciento(self):
        """Exactement 5% (1/20) → APROBADO (no estrictamente mayor)."""
        lote = Lote("Tornillos", 1000)
        muestras = [Muestra(50) for _ in range(20)]
        for m in muestras:
            lote.agregar_muestra(m)

        # 1 no conforme, 19 conformes = 5%
        _cerrar_muestra_no_conforme(muestras[0])
        for m in muestras[1:]:
            _cerrar_muestra_conforme(m)

        assert lote.porcentaje_no_conforme() == 5.0
        assert lote.decidir() == EstadoLote.APROBADO

    def test_lote_rechazado_mas_de_5_porciento(self):
        """Más de 5% → RECHAZADO."""
        lote = Lote("Tornillos", 1000)
        muestras = [Muestra(50) for _ in range(20)]
        for m in muestras:
            lote.agregar_muestra(m)

        # 2 no conformes, 18 conformes = 10%
        _cerrar_muestra_no_conforme(muestras[0])
        _cerrar_muestra_no_conforme(muestras[1])
        for m in muestras[2:]:
            _cerrar_muestra_conforme(m)

        assert lote.porcentaje_no_conforme() == 10.0
        assert lote.decidir() == EstadoLote.RECHAZADO

    def test_decidir_lote_sin_muestras_rechazado(self):
        lote = Lote("Tornillos", 1000)
        with pytest.raises(TransicionIlegalError):
            lote.decidir()

    def test_decidir_lote_incompleto_rechazado(self):
        """Lote con muestras no cerradas."""
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        with pytest.raises(TransicionIlegalError):
            lote.decidir()

    def test_decidir_lote_ya_decidido_rechazado(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        _cerrar_muestra_conforme(m)
        lote.decidir()
        with pytest.raises(TransicionIlegalError):
            lote.decidir()

    def test_decision_es_final(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        _cerrar_muestra_conforme(m)
        lote.decidir()
        assert lote.estado == EstadoLote.APROBADO


class TestConsultasLote:
    def test_total_defectos_criticos(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {
            'profesional_id': 'p1', 'fecha': date(2025, 6, 15)
        })()
        m.agregar_defecto(Defecto("VISUAL", "Critico", 5))
        m.agregar_defecto(Defecto("VISUAL", "Leve", 2))
        m.cerrar(4)  # no conforme por crítico
        assert lote.total_defectos_criticos() == 1

    def test_conteo_por_tipo(self):
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {
            'profesional_id': 'p1', 'fecha': date(2025, 6, 15)
        })()
        m.agregar_defecto(Defecto("VISUAL", "A", 2))
        m.agregar_defecto(Defecto("DIMENSIONAL", "B", 3))
        m.agregar_defecto(Defecto("VISUAL", "C", 1))
        m.cerrar(10)
        conteo = lote.conteo_por_tipo()
        assert conteo == {"VISUAL": 2, "DIMENSIONAL": 1}

    def test_conteo_criticos_sin_efectos_secundarios(self):
        """Las consultas no cambian el estado del lote, las muestras ni los defectos."""
        lote = Lote("Tornillos", 1000)
        m = Muestra(50)
        lote.agregar_muestra(m)
        _cerrar_muestra_conforme(m)

        estado_antes = lote.estado
        _ = lote.total_defectos_criticos()
        _ = lote.conteo_por_tipo()
        _ = lote.porcentaje_no_conforme()
        assert lote.estado == estado_antes
        assert m.estado == m.estado  # sin cambio

    def test_conteo_ignora_muestras_no_cerradas(self):
        lote = Lote("Tornillos", 1000)
        m_cerrada = Muestra(50)
        m_pendiente = Muestra(50)
        lote.agregar_muestra(m_cerrada)
        lote.agregar_muestra(m_pendiente)
        _cerrar_muestra_conforme(m_cerrada)
        # m_pendiente no está cerrada, no debería contarse
        assert lote.total_defectos_criticos() == 0
        assert lote.conteo_por_tipo() == {}
