"""Tests de los índices AVL por fecha de Empresa:
- equipos ordenados por fecha de calibración (vencidos, próximos a vencer);
- reportes de desviación entre dos fechas."""
import pytest
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.equipo import Equipo
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.excepciones import DatosInvalidosError

F = date(2025, 6, 15)   # fecha de referencia


@pytest.fixture
def empresa_con_equipos():
    """Equipos registrados DESORDENADOS por fecha, a propósito."""
    empresa = Empresa()
    equipos = {
        "reciente": empresa.crear_registrar_equipo("Visual", F - timedelta(days=10)),
        "vencido": empresa.crear_registrar_equipo("Visual", F - timedelta(days=200)),
        "borde_182": empresa.crear_registrar_equipo("Visual", F - timedelta(days=182)),
        "medio": empresa.crear_registrar_equipo("Dimensional", F - timedelta(days=100)),
        "borde_183": empresa.crear_registrar_equipo("Visual", F - timedelta(days=183)),
    }
    return empresa, equipos


class TestFechaVencimiento:
    def test_vence_182_dias_despues_de_calibrar(self):
        equipo = Equipo("Visual", date(2025, 1, 1))
        assert equipo.fecha_vencimiento == date(2025, 1, 1) + timedelta(days=182)
        assert equipo.esta_calibrado(equipo.fecha_vencimiento) is True
        assert equipo.esta_calibrado(equipo.fecha_vencimiento + timedelta(days=1)) is False


class TestEquiposPorCalibracion:
    def test_ordenados_del_mas_antiguo_al_mas_reciente(self, empresa_con_equipos):
        empresa, e = empresa_con_equipos
        assert empresa.equipos_por_calibracion() == [
            e["vencido"], e["borde_183"], e["borde_182"], e["medio"], e["reciente"]
        ]

    def test_vencidos_al_respeta_el_limite_de_182_dias(self, empresa_con_equipos):
        empresa, e = empresa_con_equipos
        assert empresa.equipos_vencidos_al(F) == [e["vencido"], e["borde_183"]]

    def test_vencidos_coincide_con_esta_calibrado(self, empresa_con_equipos):
        """El índice da el mismo resultado que preguntarle a cada equipo."""
        empresa, e = empresa_con_equipos
        vencidos = empresa.equipos_vencidos_al(F)
        for equipo in e.values():
            assert (equipo in vencidos) == (not equipo.esta_calibrado(F))

    def test_vencen_entre_incluye_los_extremos(self, empresa_con_equipos):
        empresa, e = empresa_con_equipos
        # borde_182 vence justo hoy (F); medio vence en F + 82 días
        assert empresa.equipos_que_vencen_entre(F, F + timedelta(days=30)) == [e["borde_182"]]
        assert empresa.equipos_que_vencen_entre(F, F + timedelta(days=90)) == [
            e["borde_182"], e["medio"]
        ]

    def test_el_que_vence_primero(self, empresa_con_equipos):
        empresa, e = empresa_con_equipos
        assert empresa.equipo_que_vence_primero(F) is e["borde_182"]

    def test_ninguno_calibrado(self):
        empresa = Empresa()
        empresa.crear_registrar_equipo("Visual", F - timedelta(days=300))
        assert empresa.equipo_que_vence_primero(F) is None

    def test_misma_fecha_de_calibracion(self):
        empresa = Empresa()
        a = empresa.crear_registrar_equipo("Visual", F - timedelta(days=300))
        b = empresa.crear_registrar_equipo("Dimensional", F - timedelta(days=300))
        assert empresa.equipos_vencidos_al(F) == [a, b]

    def test_el_indice_se_actualiza_al_registrar(self, empresa_con_equipos):
        empresa, _ = empresa_con_equipos
        nuevo = empresa.crear_registrar_equipo("Visual", F - timedelta(days=500))
        assert empresa.equipos_por_calibracion()[0] is nuevo
        assert nuevo in empresa.equipos_vencidos_al(F)

    def test_fechas_en_orden_no_desbalancean_el_arbol(self):
        """Un año de calibraciones cargadas en orden: el peor caso para un árbol
        de búsqueda sin balance (quedaría con altura 365). El AVL queda bajo."""
        empresa = Empresa()
        for dia in range(365):
            empresa.crear_registrar_equipo("Visual", date(2025, 1, 1) + timedelta(days=dia))
        arbol = empresa._equipos_por_calibracion     # acceso interno solo para el test
        assert arbol.esta_balanceado()
        assert arbol.altura() <= 10

    def test_datos_invalidos(self, empresa_con_equipos):
        empresa, _ = empresa_con_equipos
        with pytest.raises(DatosInvalidosError):
            empresa.equipos_vencidos_al("2025-06-15")
        with pytest.raises(DatosInvalidosError):
            empresa.equipos_que_vencen_entre(F + timedelta(days=10), F)

    def test_el_indice_se_conserva_al_guardar_y_cargar(self, empresa_con_equipos, tmp_path):
        empresa, _ = empresa_con_equipos
        ruta = tmp_path / "empresa.pkl"
        empresa.guardar(ruta)
        cargada = Empresa.cargar(ruta)
        assert len(cargada.equipos_vencidos_al(F)) == 2
        assert cargada.equipo_que_vence_primero(F).fecha_calibracion == F - timedelta(days=182)


@pytest.fixture
def empresa_con_reportes():
    """4 inspecciones en distintas fechas: 3 no conformes (con reporte) y 1 conforme."""
    empresa = Empresa()
    lote = empresa.crear_registrar_lote("Tornillos", 100)
    muestras = [empresa.crear_registrar_muestra(10, lote) for _ in range(4)]
    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    equipo = empresa.crear_registrar_equipo("Visual", date(2025, 5, 25))
    proc = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)

    fechas = [date(2025, 7, 1), date(2025, 6, 1), date(2025, 6, 20), date(2025, 6, 15)]
    criticas = [True, True, False, True]          # la del 20/06 queda conforme
    for muestra, fecha, critica in zip(muestras, fechas, criticas):
        insp = empresa.lanzar_inspeccion(muestra, ana, equipo, proc, fecha)
        gravedad = 5 if critica else 1
        insp.ejecutar([ObservacionVisual("Observación", True, gravedad)])
        insp.cerrar()
    return empresa


class TestReportesEntreFechas:
    def test_reportes_de_junio_ordenados_por_fecha(self, empresa_con_reportes):
        reportes = empresa_con_reportes.reportes_entre(date(2025, 6, 1), date(2025, 6, 30))
        assert list(map(lambda r: r.fecha, reportes)) == [date(2025, 6, 1), date(2025, 6, 15)]

    def test_los_extremos_se_incluyen(self, empresa_con_reportes):
        reportes = empresa_con_reportes.reportes_entre(date(2025, 6, 15), date(2025, 7, 1))
        assert list(map(lambda r: r.fecha, reportes)) == [date(2025, 6, 15), date(2025, 7, 1)]

    def test_todo_el_anio(self, empresa_con_reportes):
        assert len(empresa_con_reportes.reportes_entre(date(2025, 1, 1), date(2025, 12, 31))) == 3

    def test_periodo_sin_reportes(self, empresa_con_reportes):
        assert empresa_con_reportes.reportes_entre(date(2025, 8, 1), date(2025, 8, 31)) == []

    def test_un_solo_dia(self, empresa_con_reportes):
        assert len(empresa_con_reportes.reportes_entre(date(2025, 6, 1), date(2025, 6, 1))) == 1

    def test_arbol_de_reportes(self, empresa_con_reportes):
        arbol = empresa_con_reportes.arbol_reportes_por_fecha()
        assert len(arbol) == 3
        assert arbol.minimo()[0].fecha == date(2025, 6, 1)
        assert arbol.maximo()[0].fecha == date(2025, 7, 1)

    def test_fechas_invertidas(self, empresa_con_reportes):
        with pytest.raises(DatosInvalidosError):
            empresa_con_reportes.reportes_entre(date(2025, 6, 30), date(2025, 6, 1))

    def test_sin_reportes(self):
        assert Empresa().reportes_entre(date(2025, 1, 1), date(2025, 12, 31)) == []
