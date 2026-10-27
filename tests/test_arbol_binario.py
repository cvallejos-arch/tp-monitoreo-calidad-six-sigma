"""Tests de Árbol Binario de Búsqueda (ABB / BST - Unidad 8 EDP):
- NodoArbol: creación, getters, setters, validación, hoja, hijos.
- ArbolBinarioBusqueda: inserción, búsqueda, recorridos (in, pre, post), altura,
  mínimo, máximo, eliminación (hoja, 1 hijo, 2 hijos) y duplicados.
- Integración en el dominio: Lote.arbol_muestras_por_cantidad,
  Lote.arbol_defectos_por_gravedad, Empresa.arbol_lotes_por_produccion.
"""
from datetime import date
import pytest

from classes.nodo_arbol import NodoArbol
from classes.arbol_binario import ArbolBinarioBusqueda
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError
from classes.certificacion import Certificacion
from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual


class TestNodoArbol:
    def test_creacion_y_properties(self):
        nodo = NodoArbol(100, clave=10)
        assert nodo.get_dato() == 100
        assert nodo.get_clave() == 10
        assert nodo.get_izquierdo() is None
        assert nodo.get_derecho() is None
        assert nodo.es_hoja() is True
        assert nodo.cantidad_hijos() == 0

    def test_clave_por_defecto_es_dato(self):
        nodo = NodoArbol(55)
        assert nodo.get_clave() == 55
        assert nodo.get_dato() == 55

    def test_set_hijos_validos_e_invalidos(self):
        raiz = NodoArbol("A")
        hijo_izq = NodoArbol("B")
        hijo_der = NodoArbol("C")
        raiz.set_izquierdo(hijo_izq)
        raiz.set_derecho(hijo_der)

        assert raiz.get_izquierdo() is hijo_izq
        assert raiz.get_derecho() is hijo_der
        assert raiz.es_hoja() is False
        assert raiz.cantidad_hijos() == 2

        with pytest.raises(DatosInvalidosError):
            raiz.set_izquierdo("NoEsUnNodo")

        with pytest.raises(DatosInvalidosError):
            raiz.set_derecho(123)


class TestArbolBinarioBusqueda:
    def test_arbol_vacio(self):
        arbol = ArbolBinarioBusqueda()
        assert arbol.esta_vacio() is True
        assert len(arbol) == 0
        assert arbol.altura() == 0
        assert arbol.buscar(10) is None
        assert arbol.contiene(10) is False
        assert arbol.recorrido_in_orden() == []
        assert arbol.recorrido_pre_orden() == []
        assert arbol.recorrido_post_orden() == []

        with pytest.raises(EstructuraVaciaError):
            arbol.minimo()

        with pytest.raises(EstructuraVaciaError):
            arbol.maximo()

    def test_insercion_y_recorridos(self):
        # Insertamos claves: 50, 30, 70, 20, 40, 60, 80
        arbol = ArbolBinarioBusqueda()
        for x in [50, 30, 70, 20, 40, 60, 80]:
            arbol.insertar(f"dato_{x}", clave=x)

        assert arbol.esta_vacio() is False
        assert len(arbol) == 7
        assert arbol.altura() == 3

        # In-orden debe dar claves ordenadas: 20, 30, 40, 50, 60, 70, 80
        assert arbol.recorrido_in_orden() == [
            "dato_20", "dato_30", "dato_40", "dato_50", "dato_60", "dato_70", "dato_80"
        ]
        # Pre-orden: Raíz (50), Izq (30, 20, 40), Der (70, 60, 80)
        assert arbol.recorrido_pre_orden() == [
            "dato_50", "dato_30", "dato_20", "dato_40", "dato_70", "dato_60", "dato_80"
        ]
        # Post-orden: Izq (20, 40, 30), Der (60, 80, 70), Raíz (50)
        assert arbol.recorrido_post_orden() == [
            "dato_20", "dato_40", "dato_30", "dato_60", "dato_80", "dato_70", "dato_50"
        ]

    def test_minimo_y_maximo(self):
        arbol = ArbolBinarioBusqueda()
        for x in [15, 6, 18, 3, 7, 17, 20, 2, 4, 13, 9]:
            arbol.insertar(x, clave=x)

        assert arbol.minimo() == 2
        assert arbol.maximo() == 20

    def test_busqueda(self):
        arbol = ArbolBinarioBusqueda()
        arbol.insertar("valor_A", clave=10)
        arbol.insertar("valor_B", clave=5)
        arbol.insertar("valor_C", clave=20)

        assert arbol.buscar(10) == "valor_A"
        assert arbol.buscar(5) == "valor_B"
        assert arbol.buscar(20) == "valor_C"
        assert arbol.buscar(99) is None
        assert arbol.contiene(5) is True
        assert arbol.contiene(99) is False

    def test_duplicados_y_buscar_todos(self):
        arbol = ArbolBinarioBusqueda(permitir_duplicados=True)
        arbol.insertar("defecto_1", clave=5)
        arbol.insertar("defecto_2", clave=2)
        arbol.insertar("defecto_3", clave=5)
        arbol.insertar("defecto_4", clave=5)

        assert len(arbol) == 4
        todos_5 = arbol.buscar_todos(5)
        assert len(todos_5) == 3
        assert "defecto_1" in todos_5
        assert "defecto_3" in todos_5
        assert "defecto_4" in todos_5

    def test_iterador_python(self):
        arbol = ArbolBinarioBusqueda()
        for x in [4, 2, 6, 1, 3, 5, 7]:
            arbol.insertar(x, clave=x)

        # Iterar sobre el árbol recorre in-orden
        assert list(arbol) == [1, 2, 3, 4, 5, 6, 7]

    def test_eliminacion_hoja(self):
        arbol = ArbolBinarioBusqueda()
        for x in [50, 30, 70, 20]:
            arbol.insertar(x, clave=x)

        assert arbol.eliminar(20) is True
        assert arbol.contiene(20) is False
        assert len(arbol) == 3
        assert list(arbol) == [30, 50, 70]

    def test_eliminacion_un_hijo(self):
        arbol = ArbolBinarioBusqueda()
        for x in [50, 30, 70, 20]:  # 30 solo tiene hijo 20
            arbol.insertar(x, clave=x)

        assert arbol.eliminar(30) is True
        assert arbol.contiene(30) is False
        assert len(arbol) == 3
        assert list(arbol) == [20, 50, 70]

    def test_eliminacion_dos_hijos(self):
        arbol = ArbolBinarioBusqueda()
        for x in [50, 30, 70, 20, 40, 60, 80]:
            arbol.insertar(x, clave=x)

        # Eliminar raíz (50, tiene 2 hijos: sucesor es 60)
        assert arbol.eliminar(50) is True
        assert arbol.contiene(50) is False
        assert len(arbol) == 6
        assert list(arbol) == [20, 30, 40, 60, 70, 80]

    def test_eliminar_inexistente_retorna_false(self):
        arbol = ArbolBinarioBusqueda()
        arbol.insertar(10, clave=10)
        assert arbol.eliminar(99) is False
        assert len(arbol) == 1


class TestIntegracionArbolDominio:
    def test_lote_arbol_muestras_por_cantidad(self):
        emp = Empresa()
        lote = emp.crear_registrar_lote("Carcasas", 500)
        m1 = emp.crear_registrar_muestra(50, lote)
        m2 = emp.crear_registrar_muestra(20, lote)
        m3 = emp.crear_registrar_muestra(100, lote)

        arbol = lote.arbol_muestras_por_cantidad()
        assert len(arbol) == 3
        assert arbol.minimo() is m2  # 20
        assert arbol.maximo() is m3  # 100
        # In-orden ordenado por cantidad: 20 -> 50 -> 100
        assert list(arbol) == [m2, m1, m3]

    def test_lote_arbol_defectos_por_gravedad(self):
        emp = Empresa()
        lote = emp.crear_registrar_lote("Engranajes", 200)
        m = emp.crear_registrar_muestra(20, lote)
        prof = emp.crear_registrar_profesional("Lucas")
        prof.agregar_certificacion(Certificacion("ISO-Vis", date(2025, 1, 1), date(2025, 12, 31)))
        eq = emp.crear_registrar_equipo("Visual", date(2025, 6, 1))
        proc = emp.crear_registrar_procedimiento(
            ProcedimientoVisual,
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual",
            certificacion_requerida="ISO-Vis"
        )

        insp = emp.lanzar_siguiente_inspeccion(lote, prof, eq, proc, date(2025, 6, 15))
        # 3 defectos con gravedades 2, 5 (crítico) y 2
        insp.ejecutar([
            ObservacionVisual("Fisura leve", True, gravedad=2),
            ObservacionVisual("Rotura total", True, gravedad=5),
            ObservacionVisual("Mancha", True, gravedad=2),
        ])
        insp.cerrar()

        arbol = lote.arbol_defectos_por_gravedad()
        assert len(arbol) == 3
        # Buscar críticos directamente
        criticos = arbol.buscar_todos(5)
        assert len(criticos) == 1
        assert criticos[0].es_critico() is True
        assert criticos[0].gravedad == 5

        # Defectos con gravedad 2
        gravedad_2 = arbol.buscar_todos(2)
        assert len(gravedad_2) == 2

    def test_empresa_arbol_lotes_por_produccion(self):
        emp = Empresa()
        l1 = emp.crear_registrar_lote("Lote chico", 50)
        l2 = emp.crear_registrar_lote("Lote gigante", 1000)
        l3 = emp.crear_registrar_lote("Lote mediano", 300)

        arbol = emp.arbol_lotes_por_produccion()
        assert len(arbol) == 3
        assert arbol.minimo() is l1
        assert arbol.maximo() is l2
        assert list(arbol) == [l1, l3, l2]
