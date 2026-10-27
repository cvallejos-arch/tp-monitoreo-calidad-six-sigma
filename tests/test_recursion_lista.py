"""Tests de los métodos recursivos de ListaEnlazada (Unidad 7 EDP):
- longitud_recursiva
- buscar_recursivo
- contar_recursivo
- a_lista_recursiva
- invertir_recursivo
"""
import pytest
from classes.lista_enlazada import ListaEnlazada


class TestRecursionListaEnlazada:
    def test_longitud_recursiva_vacia(self):
        lista = ListaEnlazada()
        assert lista.longitud_recursiva() == 0

    def test_longitud_recursiva_elementos(self):
        lista = ListaEnlazada()
        for x in [10, 20, 30, 40]:
            lista.insertar_final(x)
        assert lista.longitud_recursiva() == 4
        assert lista.longitud_recursiva() == len(lista)

    def test_buscar_recursivo_en_vacia(self):
        lista = ListaEnlazada()
        assert lista.buscar_recursivo(5) is None

    def test_buscar_recursivo_encontrado_y_no_encontrado(self):
        lista = ListaEnlazada()
        for x in [10, 20, 30]:
            lista.insertar_final(x)
        nodo = lista.buscar_recursivo(20)
        assert nodo is not None
        assert nodo.get_dato() == 20
        assert lista.buscar_recursivo(99) is None

    def test_contar_recursivo(self):
        lista = ListaEnlazada()
        assert lista.contar_recursivo(5) == 0
        for x in [5, 2, 5, 8, 5]:
            lista.insertar_final(x)
        assert lista.contar_recursivo(5) == 3
        assert lista.contar_recursivo(2) == 1
        assert lista.contar_recursivo(99) == 0

    def test_a_lista_recursiva(self):
        lista = ListaEnlazada()
        assert lista.a_lista_recursiva() == []
        for x in [1, 2, 3]:
            lista.insertar_final(x)
        assert lista.a_lista_recursiva() == [1, 2, 3]

    def test_invertir_recursivo_vacia_y_un_elemento(self):
        vacia = ListaEnlazada()
        vacia.invertir_recursivo()
        assert vacia.esta_vacia() is True

        uno = ListaEnlazada()
        uno.insertar_final(42)
        uno.invertir_recursivo()
        assert uno.primero() == 42
        assert uno.ultimo() == 42
        assert len(uno) == 1

    def test_invertir_recursivo_multiples_elementos(self):
        lista = ListaEnlazada()
        for x in [1, 2, 3, 4]:
            lista.insertar_final(x)
        lista.invertir_recursivo()
        assert list(lista) == [4, 3, 2, 1]
        assert lista.primero() == 4
        assert lista.ultimo() == 1
        assert len(lista) == 4
