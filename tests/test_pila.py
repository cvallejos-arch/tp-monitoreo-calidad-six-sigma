"""Tests de Pila (LIFO): el último en entrar es el primero en salir.
Operaciones de la materia: push, pop, peek, isEmpty, size."""
import pytest

from classes.pila import Pila
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


@pytest.fixture
def pila_1_2_3():
    """Pila donde se hizo push de 1, 2 y 3 (top = 3)."""
    pila = Pila()
    pila.push(1)
    pila.push(2)
    pila.push(3)
    return pila


class TestPilaVacia:
    def test_nueva_pila_esta_vacia(self):
        pila = Pila()
        assert pila.isEmpty() is True
        assert pila.size() == 0
        assert len(pila) == 0

    def test_pop_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Pila().pop()

    def test_peek_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Pila().peek()

    def test_historial_vacio(self):
        assert Pila().historial() == ()


class TestOrdenLIFO:
    def test_peek_es_el_ultimo_agregado(self, pila_1_2_3):
        assert pila_1_2_3.peek() == 3

    def test_peek_no_elimina(self, pila_1_2_3):
        pila_1_2_3.peek()
        assert pila_1_2_3.size() == 3

    def test_pop_en_orden_inverso(self, pila_1_2_3):
        assert pila_1_2_3.pop() == 3
        assert pila_1_2_3.pop() == 2
        assert pila_1_2_3.pop() == 1
        assert pila_1_2_3.isEmpty() is True

    def test_push_despues_de_pop(self, pila_1_2_3):
        pila_1_2_3.pop()
        pila_1_2_3.push(9)
        assert pila_1_2_3.peek() == 9
        assert pila_1_2_3.size() == 3

    def test_size_y_len_coinciden(self, pila_1_2_3):
        assert pila_1_2_3.size() == len(pila_1_2_3) == 3


class TestHistorialEIteracion:
    def test_historial_del_bottom_al_top(self, pila_1_2_3):
        assert pila_1_2_3.historial() == (1, 2, 3)

    def test_historial_es_tupla(self, pila_1_2_3):
        assert isinstance(pila_1_2_3.historial(), tuple)

    def test_iterar_del_top_al_bottom(self, pila_1_2_3):
        assert list(pila_1_2_3) == [3, 2, 1]

    def test_filter_sobre_pila(self, pila_1_2_3):
        assert list(filter(lambda x: x > 1, pila_1_2_3)) == [3, 2]


class TestTipoPila:
    def test_tipo_indicado_rechaza_otro_tipo(self):
        pila = Pila(int)
        with pytest.raises(DatosInvalidosError):
            pila.push("x")

    def test_repr(self, pila_1_2_3):
        assert repr(pila_1_2_3) == "Pila(size=3)"
