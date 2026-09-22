"""Tests de Muestra: transiciones de estado, immutabilidad, reinspection."""
import pytest
from datetime import date

from classes.muestra import Muestra
from classes.defecto import Defecto
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError, TransicionIlegalError


class TestCreacionMuestra:
    def test_creacion_valida(self):
        m = Muestra(50)
        assert m.cantidad == 50
        assert m.estado == EstadoMuestra.PENDIENTE
        assert m.defectos == ()
        assert m.lote_id is None
        assert m.reporte is None

    def test_cantidad_cero_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Muestra(0)

    def test_cantidad_negativa_rechazada(self):
        with pytest.raises(DatosInvalidosError):
            Muestra(-1)


class TestTransiciones:
    def test_iniciar_inspeccion(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        assert m.estado == EstadoMuestra.EN_INSPECCION

    def test_iniciar_inspeccion_dos_veces_rechazado(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        with pytest.raises(TransicionIlegalError):
            m.iniciar_inspeccion()

    def test_agregar_defecto_en_inspeccion(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        d = Defecto("VISUAL", "Rayadura", 2)
        m.agregar_defecto(d)
        assert len(m.defectos) == 1

    def test_agregar_defecto_en_pendiente_rechazado(self):
        m = Muestra(50)
        with pytest.raises(TransicionIlegalError):
            m.agregar_defecto(Defecto("VISUAL", "Test", 1))


class TestConformidad:
    def test_conforme_sin_defectos(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        # Simulamos asignar inspección creando un mock mínimo
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.cerrar(5)
        assert m.estado == EstadoMuestra.CONFORME
        assert m.reporte is None

    def test_conforme_suma_igual_al_limite(self):
        """Suma de gravedades = límite → CONFORME (no estrictamente mayor)."""
        m = Muestra(50)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.agregar_defecto(Defecto("VISUAL", "Leve", 2))
        m.agregar_defecto(Defecto("VISUAL", "Media", 3))
        # suma = 5, límite = 5 → conforme (no estrictamente mayor)
        m.cerrar(5)
        assert m.estado == EstadoMuestra.CONFORME

    def test_no_conforme_suma_mayor_al_limite(self):
        """Suma de gravedades > límite → NO_CONFORME."""
        m = Muestra(50)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.agregar_defecto(Defecto("VISUAL", "Leve", 2))
        m.agregar_defecto(Defecto("VISUAL", "Alta", 4))
        # suma = 6, límite = 5 → no conforme
        m.cerrar(5)
        assert m.estado == EstadoMuestra.NO_CONFORME
        assert m.reporte is not None

    def test_no_conforme_con_defecto_critico(self):
        """Defecto de gravedad 5 → NO_CONFORME sin importar el límite."""
        m = Muestra(50)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.agregar_defecto(Defecto("VISUAL", "Critico", 5))
        # gravedad 5 es critico → no conforme aunque suma(5) <= limite(10)
        m.cerrar(10)
        assert m.estado == EstadoMuestra.NO_CONFORME


class TestInmutabilidadAlCerrar:
    def test_no_agregar_defecto_despues_de_cerrar(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.cerrar(5)
        with pytest.raises(TransicionIlegalError):
            m.agregar_defecto(Defecto("VISUAL", "Test", 1))

    def test_no_cerrar_dos_veces(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        m._inspeccion = type('obj', (object,), {'profesional_id': 'p1', 'fecha': date(2025, 6, 15)})()
        m._lote_id = 'L1'
        m.cerrar(5)
        with pytest.raises(TransicionIlegalError):
            m.cerrar(5)

    def test_defectos_retorna_tupla(self):
        """Los defectos retornados son una tupla inmutable."""
        m = Muestra(50)
        m.iniciar_inspeccion()
        d = Defecto("VISUAL", "Rayadura", 2)
        m.agregar_defecto(d)
        assert isinstance(m.defectos, tuple)


class TestPertenenciaLote:
    def test_asignar_lote(self):
        m = Muestra(50)
        m.asignar_lote("L1")
        assert m.lote_id == "L1"

    def test_no_mover_a_otro_lote(self):
        m = Muestra(50)
        m.asignar_lote("L1")
        with pytest.raises(TransicionIlegalError):
            m.asignar_lote("L2")


class TestCalculos:
    def test_suma_gravedades(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        m.agregar_defecto(Defecto("VISUAL", "A", 2))
        m.agregar_defecto(Defecto("VISUAL", "B", 3))
        assert m.suma_gravedades() == 5

    def test_tiene_critico_true(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        m.agregar_defecto(Defecto("VISUAL", "Critico", 5))
        assert m.tiene_critico() is True

    def test_tiene_critico_false(self):
        m = Muestra(50)
        m.iniciar_inspeccion()
        m.agregar_defecto(Defecto("VISUAL", "Leve", 4))
        assert m.tiene_critico() is False
