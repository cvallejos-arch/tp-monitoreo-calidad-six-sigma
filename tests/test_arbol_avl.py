"""Tests del árbol AVL (NodoAVL y ArbolAVL): búsqueda, las 4 rotaciones,
balance después de insertar y eliminar, recorridos, claves repetidas, y los
índices del dominio (Lote y Empresa)."""
import pytest
from datetime import date

from classes.nodo_avl import NodoAVL
from classes.arbol_avl import ArbolAVL
from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


def _arbol(*claves):
    """Árbol con esas claves; cada dato es el texto de su clave."""
    arbol = ArbolAVL()
    for clave in claves:
        arbol.insertar(clave, f"d{clave}")
    return arbol


class TestNodoAVL:
    def test_nodo_nuevo_es_hoja_de_altura_1(self):
        nodo = NodoAVL(10, "dato")
        assert nodo.get_clave() == 10
        assert nodo.get_datos() == ("dato",)
        assert nodo.get_altura() == 1
        assert nodo.es_hoja()

    def test_agregar_dato_con_la_misma_clave(self):
        nodo = NodoAVL(2, "a")
        nodo.agregar_dato("b")
        assert nodo.get_datos() == ("a", "b")

    def test_hijos_tienen_que_ser_nodos(self):
        nodo = NodoAVL(10, "x")
        nodo.set_izquierdo(NodoAVL(5, "y"))
        assert not nodo.es_hoja()
        with pytest.raises(DatosInvalidosError):
            nodo.set_derecho("no es un nodo")


class TestBuscar:
    def test_buscar_existente_devuelve_sus_datos(self):
        assert _arbol(10, 5, 15).buscar(5) == ("d5",)

    def test_buscar_inexistente_devuelve_tupla_vacia(self):
        assert _arbol(10, 5, 15).buscar(99) == ()

    def test_buscar_en_arbol_vacio(self):
        assert ArbolAVL().buscar(1) == ()

    def test_contiene(self):
        arbol = _arbol(10, 5, 15)
        assert arbol.contiene(15) is True
        assert arbol.contiene(7) is False

    def test_buscar_rango_incluye_extremos_y_ordena(self):
        arbol = _arbol(50, 20, 80, 10, 30, 70, 90)
        assert arbol.buscar_rango(20, 70) == ["d20", "d30", "d50", "d70"]

    def test_buscar_rango_sin_resultados(self):
        assert _arbol(10, 20, 30).buscar_rango(21, 29) == []

    def test_buscar_con_fechas(self):
        arbol = ArbolAVL()
        arbol.insertar(date(2025, 3, 1), "marzo")
        arbol.insertar(date(2025, 1, 1), "enero")
        arbol.insertar(date(2025, 6, 1), "junio")
        assert arbol.buscar(date(2025, 1, 1)) == ("enero",)
        assert arbol.buscar_rango(date(2025, 2, 1), date(2025, 12, 31)) == ["marzo", "junio"]


class TestRotaciones:
    """Los 4 casos del apunte. niveles() muestra la forma del árbol (BFS)."""

    def test_izquierda_izquierda_rotacion_simple_derecha(self):
        assert _arbol(30, 20, 10).niveles() == [[20], [10, 30]]

    def test_derecha_derecha_rotacion_simple_izquierda(self):
        assert _arbol(10, 20, 30).niveles() == [[20], [10, 30]]

    def test_izquierda_derecha_rotacion_doble(self):
        assert _arbol(30, 10, 20).niveles() == [[20], [10, 30]]

    def test_derecha_izquierda_rotacion_doble(self):
        assert _arbol(10, 30, 20).niveles() == [[20], [10, 30]]

    def test_secuencia_del_apunte(self):
        """10, 20, 30, 40, 50 destruiría un ABB común (quedaría una cadena de altura 5)."""
        arbol = _arbol(10, 20, 30, 40, 50)
        assert arbol.niveles() == [[20], [10, 40], [30, 50]]
        assert arbol.altura() == 3


class TestBalance:
    def test_claves_ordenadas_dan_altura_logaritmica(self):
        arbol = _arbol(*range(1, 1001))
        assert arbol.esta_balanceado()
        assert arbol.altura() <= 11        # un ABB sin balance tendría altura 1000

    def test_claves_en_orden_descendente(self):
        arbol = _arbol(*range(500, 0, -1))
        assert arbol.esta_balanceado()
        assert arbol.claves_in_orden() == list(range(1, 501))

    def test_sigue_balanceado_despues_de_eliminar(self):
        arbol = _arbol(*range(1, 201))
        for clave in range(1, 201, 3):
            arbol.eliminar(clave)
            assert arbol.esta_balanceado()
        assert arbol.claves_in_orden() == [c for c in range(1, 201) if c % 3 != 1]

    def test_eliminar_puede_provocar_rotacion(self):
        arbol = _arbol(20, 10, 30, 40)       # 40 cuelga a la derecha de 30
        arbol.eliminar(10)                    # la raíz queda cargada a la derecha
        assert arbol.niveles() == [[30], [20, 40]]


class TestClavesRepetidas:
    def test_misma_clave_mismo_nodo(self):
        arbol = ArbolAVL()
        for dato in ("a", "b", "c"):
            arbol.insertar(2, dato)
        assert arbol.buscar(2) == ("a", "b", "c")
        assert len(arbol) == 3
        assert arbol.cantidad_nodos() == 1

    def test_eliminar_quita_todos_los_datos_de_la_clave(self):
        arbol = ArbolAVL()
        arbol.insertar(2, "a")
        arbol.insertar(2, "b")
        arbol.insertar(5, "c")
        assert arbol.eliminar(2) is True
        assert len(arbol) == 1
        assert arbol.buscar(2) == ()


class TestEliminar:
    def test_eliminar_hoja(self):
        arbol = _arbol(10, 5, 15)
        assert arbol.eliminar(5) is True
        assert arbol.claves_in_orden() == [10, 15]

    def test_eliminar_nodo_con_un_hijo(self):
        arbol = _arbol(10, 5, 15, 20)
        arbol.eliminar(15)
        assert arbol.claves_in_orden() == [5, 10, 20]
        assert arbol.esta_balanceado()

    def test_eliminar_nodo_con_dos_hijos_usa_el_sucesor(self):
        arbol = _arbol(20, 10, 30, 25, 35)
        arbol.eliminar(30)                   # su lugar lo toma 35 (mínimo de la derecha)
        assert arbol.claves_in_orden() == [10, 20, 25, 35]
        assert arbol.buscar(35) == ("d35",)
        assert arbol.esta_balanceado()

    def test_eliminar_la_raiz(self):
        arbol = _arbol(20, 10, 30)
        arbol.eliminar(20)
        assert arbol.claves_in_orden() == [10, 30]

    def test_eliminar_inexistente(self):
        arbol = _arbol(10, 5)
        assert arbol.eliminar(99) is False
        assert len(arbol) == 2


class TestRecorridosYConsultas:
    def test_arbol_vacio(self):
        arbol = ArbolAVL()
        assert arbol.esta_vacio()
        assert len(arbol) == 0
        assert arbol.altura() == 0
        assert arbol.recorrido_in_orden() == []
        assert arbol.niveles() == []
        with pytest.raises(EstructuraVaciaError):
            arbol.minimo()
        with pytest.raises(EstructuraVaciaError):
            arbol.maximo()

    def test_recorridos(self):
        arbol = _arbol(20, 10, 30, 5, 15)
        #        20
        #       /  \
        #     10    30
        #    /  \
        #   5    15
        assert arbol.recorrido_in_orden() == ["d5", "d10", "d15", "d20", "d30"]
        assert arbol.recorrido_pre_orden() == ["d20", "d10", "d5", "d15", "d30"]
        assert arbol.recorrido_post_orden() == ["d5", "d15", "d10", "d30", "d20"]
        assert arbol.niveles() == [[20], [10, 30], [5, 15]]

    def test_minimo_y_maximo(self):
        arbol = _arbol(50, 20, 80, 10, 90)
        assert arbol.minimo() == ("d10",)
        assert arbol.maximo() == ("d90",)

    def test_iterar_en_orden(self):
        assert list(_arbol(3, 1, 2)) == ["d1", "d2", "d3"]

    def test_repr(self):
        assert repr(_arbol(1, 2, 3)) == "ArbolAVL(datos=3, claves=3, altura=2)"


class TestClavesInvalidas:
    def test_clave_none(self):
        with pytest.raises(DatosInvalidosError):
            ArbolAVL().insertar(None, "x")

    def test_claves_que_no_se_pueden_comparar(self):
        arbol = _arbol(10)
        with pytest.raises(DatosInvalidosError):
            arbol.insertar("diez", "x")
        assert len(arbol) == 1               # el árbol no cambió


class TestIndicesDelDominio:
    def test_lote_arbol_muestras_por_cantidad(self):
        emp = Empresa()
        lote = emp.crear_registrar_lote("Carcasas", 500)
        m1 = emp.crear_registrar_muestra(50, lote)
        m2 = emp.crear_registrar_muestra(20, lote)
        m3 = emp.crear_registrar_muestra(100, lote)
        m4 = emp.crear_registrar_muestra(50, lote)

        arbol = lote.arbol_muestras_por_cantidad()
        assert len(arbol) == 4
        assert arbol.cantidad_nodos() == 3          # 20, 50 y 100
        assert arbol.minimo() == (m2,)
        assert arbol.maximo() == (m3,)
        assert arbol.buscar(50) == (m1, m4)
        assert list(arbol) == [m2, m1, m4, m3]

    def test_lote_arbol_defectos_por_gravedad(self):
        emp = Empresa()
        lote = emp.crear_registrar_lote("Engranajes", 200)
        emp.crear_registrar_muestra(20, lote)
        prof = emp.crear_registrar_profesional("Lucas")
        prof.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
        equipo = emp.crear_registrar_equipo("Visual", date(2025, 6, 1))
        proc = emp.crear_registrar_procedimiento(
            ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")

        insp = emp.lanzar_siguiente_inspeccion(lote, prof, equipo, proc, date(2025, 6, 15))
        insp.ejecutar([
            ObservacionVisual("Fisura leve", True, 2),
            ObservacionVisual("Rotura total", True, 5),
            ObservacionVisual("Mancha", True, 2),
        ])
        insp.cerrar()

        arbol = lote.arbol_defectos_por_gravedad()
        assert len(arbol) == 3
        assert arbol.cantidad_nodos() == 2          # gravedades 2 y 5
        criticos = arbol.buscar(5)
        assert len(criticos) == 1 and criticos[0].es_critico()
        assert len(arbol.buscar(2)) == 2
        assert arbol.buscar_rango(3, 5) == list(criticos)

    def test_arbol_defectos_ignora_muestras_abiertas(self):
        emp = Empresa()
        lote = emp.crear_registrar_lote("Engranajes", 200)
        emp.crear_registrar_muestra(20, lote)
        assert len(lote.arbol_defectos_por_gravedad()) == 0

    def test_empresa_arbol_lotes_por_produccion(self):
        emp = Empresa()
        l1 = emp.crear_registrar_lote("Lote chico", 50)
        l2 = emp.crear_registrar_lote("Lote gigante", 1000)
        l3 = emp.crear_registrar_lote("Lote mediano", 300)

        arbol = emp.arbol_lotes_por_produccion()
        assert len(arbol) == 3
        assert arbol.minimo() == (l1,)
        assert arbol.maximo() == (l2,)
        assert list(arbol) == [l1, l3, l2]
        assert arbol.buscar_rango(100, 500) == [l3]
