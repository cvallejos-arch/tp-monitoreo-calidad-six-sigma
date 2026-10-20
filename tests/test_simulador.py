"""Tests del Simulador (aleatoriedad con semilla). Todos usan semillas fijas:
el resultado es siempre el mismo, así que los tests nunca fallan por azar."""
import pytest
from datetime import date, timedelta

from classes.simulador import Simulador
from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.estado_muestra import EstadoMuestra
from classes.estado_lote import EstadoLote
from classes.excepciones import DatosInvalidosError, CertificacionNoVigenteError

FECHA = date(2025, 6, 15)


def _resumen_visual(observaciones):
    return list(map(lambda o: (o.descripcion, o.defecto_detectado, o.gravedad), observaciones))


def _contexto(cantidad_muestras=10):
    """Empresa con un lote, una profesional certificada, equipos y procedimientos."""
    empresa = Empresa()
    lote = empresa.crear_registrar_lote("Tornillos", 1000)
    for _ in range(cantidad_muestras):
        empresa.crear_registrar_muestra(10, lote)
    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    visual = empresa.crear_registrar_equipo("Visual", FECHA - timedelta(days=10))
    dimensional = empresa.crear_registrar_equipo("Dimensional", FECHA - timedelta(days=10))
    proc_v = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")
    proc_d = empresa.crear_registrar_procedimiento(
        ProcedimientoDimensional, limite_gravedad_acumulada=5)
    return empresa, lote, ana, visual, dimensional, proc_v, proc_d


class TestSemilla:
    def test_misma_semilla_mismas_observaciones(self):
        a = Simulador(42).observaciones_visuales(20, prob_defecto=0.5)
        b = Simulador(42).observaciones_visuales(20, prob_defecto=0.5)
        assert _resumen_visual(a) == _resumen_visual(b)

    def test_distinta_semilla_distintas_observaciones(self):
        a = Simulador(1).observaciones_visuales(20, prob_defecto=0.5)
        b = Simulador(2).observaciones_visuales(20, prob_defecto=0.5)
        assert _resumen_visual(a) != _resumen_visual(b)

    def test_guarda_la_semilla(self):
        assert Simulador(7).semilla == 7
        assert Simulador().semilla is None

    def test_no_altera_el_random_global(self):
        import random
        random.seed(123)
        esperado = random.random()
        random.seed(123)
        Simulador(5).observaciones_visuales(10)
        assert random.random() == esperado


class TestObservacionesVisuales:
    def test_cantidad_y_tipo(self):
        obs = Simulador(1).observaciones_visuales(15)
        assert len(obs) == 15
        assert all(map(lambda o: isinstance(o, ObservacionVisual), obs))

    def test_probabilidad_cero_sin_defectos(self):
        obs = Simulador(1).observaciones_visuales(30, prob_defecto=0)
        assert not any(map(lambda o: o.defecto_detectado, obs))

    def test_probabilidad_uno_todos_con_defecto(self):
        obs = Simulador(1).observaciones_visuales(30, prob_defecto=1)
        assert all(map(lambda o: o.defecto_detectado, obs))

    def test_gravedades_entre_1_y_5(self):
        obs = Simulador(3).observaciones_visuales(200, prob_defecto=1)
        gravedades = set(map(lambda o: o.gravedad, obs))
        assert gravedades <= {1, 2, 3, 4, 5}
        assert len(gravedades) == 5   # con 200 casos aparecen todas

    @pytest.mark.parametrize("prob", [-0.1, 1.5, "0.5", True])
    def test_probabilidad_invalida(self, prob):
        with pytest.raises(DatosInvalidosError):
            Simulador(1).observaciones_visuales(5, prob_defecto=prob)

    @pytest.mark.parametrize("cantidad", [0, -3, 2.5])
    def test_cantidad_invalida(self, cantidad):
        with pytest.raises(DatosInvalidosError):
            Simulador(1).observaciones_visuales(cantidad)


class TestObservacionesDimensionales:
    def test_valores_dentro_del_margen(self):
        obs = Simulador(4).observaciones_dimensionales(100, 9.0, 10.0, dispersion=0.2)
        assert all(map(lambda o: isinstance(o, ObservacionDimensional), obs))
        assert all(map(lambda o: 8.8 <= o.valor_medido <= 10.2, obs))

    def test_dispersion_cero_nunca_sale_de_tolerancia(self):
        obs = Simulador(4).observaciones_dimensionales(50, 9.0, 10.0, dispersion=0)
        assert all(map(lambda o: o.desviacion == 0, obs))

    def test_con_dispersion_algunas_quedan_fuera(self):
        obs = Simulador(4).observaciones_dimensionales(100, 9.0, 10.0, dispersion=0.5)
        fuera = list(filter(lambda o: o.desviacion > 0, obs))
        assert 0 < len(fuera) < 100

    def test_tolerancias_invertidas(self):
        with pytest.raises(DatosInvalidosError):
            Simulador(1).observaciones_dimensionales(5, 10.0, 9.0)


class TestObservacionesPara:
    def test_elige_el_tipo_segun_el_procedimiento(self):
        sim = Simulador(1)
        visuales = sim.observaciones_para(ProcedimientoVisual(limite_gravedad_acumulada=5), 3)
        dimensionales = sim.observaciones_para(
            ProcedimientoDimensional(limite_gravedad_acumulada=5), 3)
        assert all(map(lambda o: isinstance(o, ObservacionVisual), visuales))
        assert all(map(lambda o: isinstance(o, ObservacionDimensional), dimensionales))


class TestSimularLote:
    def test_inspecciona_todas_las_muestras(self):
        empresa, lote, ana, visual, _, proc_v, _ = _contexto(10)
        inspecciones = Simulador(42).simular_lote(empresa, lote, ana, visual, proc_v, FECHA,
                                                  prob_defecto=0.3)
        assert len(inspecciones) == 10
        assert lote.todas_cerradas()
        assert lote.siguiente_muestra_pendiente() is None

    def test_misma_semilla_mismo_resultado_del_lote(self):
        resultados = []
        for _ in range(2):
            empresa, lote, ana, visual, _, proc_v, _ = _contexto(20)
            Simulador(42).simular_lote(empresa, lote, ana, visual, proc_v, FECHA,
                                       prob_defecto=0.3)
            resultados.append((list(map(lambda m: m.estado, lote.muestras)), lote.decidir()))
        assert resultados[0] == resultados[1]

    def test_probabilidad_cero_lote_aprobado(self):
        empresa, lote, ana, visual, _, proc_v, _ = _contexto(10)
        Simulador(1).simular_lote(empresa, lote, ana, visual, proc_v, FECHA, prob_defecto=0)
        assert all(map(lambda m: m.estado == EstadoMuestra.CONFORME, lote.muestras))
        assert lote.decidir() == EstadoLote.APROBADO

    def test_simulacion_dimensional(self):
        empresa, lote, ana, _, dimensional, _, proc_d = _contexto(10)
        Simulador(8).simular_lote(empresa, lote, ana, dimensional, proc_d, FECHA,
                                  dispersion=0.5)
        assert lote.todas_cerradas()
        assert lote.decidir() in (EstadoLote.APROBADO, EstadoLote.RECHAZADO)

    def test_las_validaciones_del_dominio_se_aplican(self):
        """Un profesional sin la certificación no puede inspeccionar, ni siquiera simulando."""
        empresa, lote, _, visual, _, proc_v, _ = _contexto(3)
        carlos = empresa.crear_registrar_profesional("Carlos")
        with pytest.raises(CertificacionNoVigenteError):
            Simulador(1).simular_lote(empresa, lote, carlos, visual, proc_v, FECHA)
        # La validación falló antes de iniciar: ninguna muestra quedó a medias
        assert all(map(lambda m: m.estado == EstadoMuestra.PENDIENTE, lote.muestras))

    def test_lote_sin_pendientes_no_hace_nada(self):
        empresa, lote, ana, visual, _, proc_v, _ = _contexto(0)
        assert Simulador(1).simular_lote(empresa, lote, ana, visual, proc_v, FECHA) == []
