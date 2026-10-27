"""Tests de ColaPrioridad (max-heap): las fórmulas de índice, los dos invariantes
(forma y orden), el orden de salida, los empates, y la cola de atención de
reportes de Empresa."""
import random
import pytest
from datetime import date

from classes.cola_prioridad import ColaPrioridad
from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError

PACIENTES = [                       # el ejemplo del notebook de la cátedra
    ("Dolor de pecho", 9),
    ("Guardia de rutina", 3),
    ("Quemadura grave", 8),
    ("Esguince de tobillo", 2),
    ("Fiebre alta", 7),
    ("Fractura expuesta", 10),
    ("Revisión de yeso", 4),
]


def _cola(*pares):
    cola = ColaPrioridad()
    for valor, prioridad in pares:
        cola.insertar(valor, prioridad)
    return cola


def _cumple_orden(cola):
    """Invariante de orden: ningún hijo sale antes que su padre."""
    return all(map(lambda i: not cola._es_mayor(i, cola.padre(i)), range(1, len(cola))))


class TestNavegacion:
    def test_formulas_de_indice(self):
        cola = _cola(*PACIENTES)                         # 7 elementos: índices 0 a 6
        assert cola.padre(0) is None
        assert cola.padre(3) == 1 and cola.padre(4) == 1
        assert cola.hijo_izq(1) == 3 and cola.hijo_der(1) == 4
        assert cola.hijo_izq(3) is None                  # 7 no existe

    def test_intercambiar(self):
        cola = _cola(("a", 1), ("b", 2))
        primero = cola._datos[0]["valor"]
        cola.intercambiar(0, 1)
        assert cola._datos[1]["valor"] == primero


class TestOrdenDeSalida:
    def test_ejemplo_de_la_sala_de_urgencias(self):
        cola = _cola(*PACIENTES)
        assert cola.ver_maximo() == "Fractura expuesta"
        salida = []
        while cola:                                      # __bool__
            salida.append(cola.extraer_maximo())
        assert salida == ["Fractura expuesta", "Dolor de pecho", "Quemadura grave",
                          "Fiebre alta", "Revisión de yeso", "Guardia de rutina",
                          "Esguince de tobillo"]

    def test_ver_maximo_no_quita(self):
        cola = _cola(*PACIENTES)
        cola.ver_maximo()
        assert len(cola) == 7

    def test_prioridad_maxima(self):
        assert _cola(*PACIENTES).prioridad_maxima() == 10

    def test_empate_sale_primero_el_que_llego_antes(self):
        cola = _cola(("primero", 5), ("segundo", 5), ("urgente", 9), ("tercero", 5))
        assert cola.en_orden_de_prioridad() == ["urgente", "primero", "segundo", "tercero"]

    def test_prioridad_con_tuplas(self):
        cola = _cola(("leve", (2, 3)), ("critico", (5, 5)), ("grave", (4, 9)),
                     ("critico y mas", (5, 8)))
        assert cola.en_orden_de_prioridad() == ["critico y mas", "critico", "grave", "leve"]

    def test_en_orden_de_prioridad_no_vacia_la_cola(self):
        cola = _cola(*PACIENTES)
        cola.en_orden_de_prioridad()
        assert len(cola) == 7
        assert cola.extraer_maximo() == "Fractura expuesta"

    def test_insertar_despues_de_extraer(self):
        cola = _cola(("a", 5), ("b", 3))
        cola.extraer_maximo()
        cola.insertar("c", 4)
        assert cola.en_orden_de_prioridad() == ["c", "b"]


class TestInvariantes:
    def test_el_orden_se_mantiene_en_cada_paso(self):
        rng = random.Random(42)                          # semilla fija: siempre igual
        cola = ColaPrioridad()
        for i in range(200):
            cola.insertar(f"x{i}", rng.randint(1, 50))
            assert _cumple_orden(cola)
        anterior = None
        while cola:
            prioridad = cola.prioridad_maxima()
            cola.extraer_maximo()
            assert _cumple_orden(cola)
            assert anterior is None or prioridad <= anterior   # salen de mayor a menor
            anterior = prioridad

    def test_la_lista_no_tiene_huecos(self):
        """Invariante de forma: el árbol es completo, la lista ocupa 0..n-1."""
        cola = _cola(*PACIENTES)
        cola.extraer_maximo()
        assert len(cola._datos) == 6
        assert all(map(lambda d: d is not None, cola._datos))


class TestCasosLimite:
    def test_cola_vacia(self):
        cola = ColaPrioridad()
        assert cola.esta_vacia() and not cola and len(cola) == 0
        assert cola.en_orden_de_prioridad() == []

    @pytest.mark.parametrize("operacion", ["extraer_maximo", "ver_maximo", "prioridad_maxima"])
    def test_operaciones_sobre_cola_vacia(self, operacion):
        with pytest.raises(EstructuraVaciaError):
            getattr(ColaPrioridad(), operacion)()

    def test_un_solo_elemento(self):
        cola = _cola(("solo", 1))
        assert cola.extraer_maximo() == "solo"
        assert cola.esta_vacia()

    @pytest.mark.parametrize("prioridad", ["alta", None, True, [1, 2]])
    def test_prioridad_invalida(self, prioridad):
        with pytest.raises(DatosInvalidosError):
            ColaPrioridad().insertar("x", prioridad)

    def test_repr(self):
        assert repr(_cola(("a", 1), ("b", 2))) == "ColaPrioridad(tamanio=2)"


class TestAtencionDeReportes:
    @pytest.fixture
    def empresa(self):
        """4 reportes: dos con crítico (mismo nivel, distinta suma), uno grave y uno
        crítico que empata con otro en todo pero es más nuevo."""
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        ana = empresa.crear_registrar_profesional("Ana")
        ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
        equipo = empresa.crear_registrar_equipo("Visual", date(2025, 5, 25))
        proc = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)

        casos = [                                     # (fecha, gravedades)
            (date(2025, 6, 10), [3, 3]),              # grave, sin crítico: (3, 6)
            (date(2025, 6, 5), [5]),                  # crítico solo: (5, 5)
            (date(2025, 6, 20), [5, 2]),              # crítico con más defectos: (5, 7)
            (date(2025, 6, 25), [5]),                 # empata con el del 5/6, pero es más nuevo
        ]
        for fecha, gravedades in casos:
            muestra = empresa.crear_registrar_muestra(10, lote)
            insp = empresa.lanzar_inspeccion(muestra, ana, equipo, proc, fecha)
            insp.ejecutar(list(map(lambda g: ObservacionVisual(f"Defecto {g}", True, g), gravedades)))
            insp.cerrar()
        return empresa

    def test_gravedad_maxima_y_suma_del_reporte(self, empresa):
        reporte = empresa.reportes_entre(date(2025, 6, 20), date(2025, 6, 20))[0]
        assert reporte.gravedad_maxima == 5
        assert reporte.suma_gravedades == 7

    def test_orden_de_atencion(self, empresa):
        cola = empresa.cola_atencion_reportes()
        fechas = list(map(lambda r: r.fecha, cola.en_orden_de_prioridad()))
        assert fechas == [date(2025, 6, 20),   # (5, 7): crítico y mayor suma
                          date(2025, 6, 5),    # (5, 5): crítico, llegó antes
                          date(2025, 6, 25),   # (5, 5): crítico, llegó después
                          date(2025, 6, 10)]   # (3, 6): sin crítico, al final

    def test_atender_el_mas_grave(self, empresa):
        cola = empresa.cola_atencion_reportes()
        assert cola.prioridad_maxima() == (5, 7)
        assert cola.extraer_maximo().fecha == date(2025, 6, 20)
        assert len(cola) == 3

    def test_solo_los_reportes_del_periodo(self, empresa):
        cola = empresa.cola_atencion_reportes(date(2025, 6, 1), date(2025, 6, 15))
        fechas = list(map(lambda r: r.fecha, cola.en_orden_de_prioridad()))
        assert fechas == [date(2025, 6, 5), date(2025, 6, 10)]

    def test_periodo_con_fechas_invertidas(self, empresa):
        with pytest.raises(DatosInvalidosError):
            empresa.cola_atencion_reportes(date(2025, 6, 30), date(2025, 6, 1))

    def test_sin_reportes(self):
        assert Empresa().cola_atencion_reportes().esta_vacia()
