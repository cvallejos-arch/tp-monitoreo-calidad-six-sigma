"""Tests de Pila (LIFO): el último en entrar es el primero en salir."""
import pytest

from classes.pila import Pila
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


@pytest.fixture
def pila_1_2_3():
    """Pila donde se apilaron 1, 2 y 3 (tope = 3)."""
    pila = Pila()
    pila.apilar(1)
    pila.apilar(2)
    pila.apilar(3)
    return pila


class TestPilaVacia:
    def test_nueva_pila_esta_vacia(self):
        pila = Pila()
        assert pila.esta_vacia() is True
        assert len(pila) == 0

    def test_desapilar_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Pila().desapilar()

    def test_tope_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Pila().tope()

    def test_historial_vacio(self):
        assert Pila().historial() == ()


class TestOrdenLIFO:
    def test_tope_es_el_ultimo_apilado(self, pila_1_2_3):
        assert pila_1_2_3.tope() == 3

    def test_tope_no_elimina(self, pila_1_2_3):
        pila_1_2_3.tope()
        assert len(pila_1_2_3) == 3

    def test_desapilar_en_orden_inverso(self, pila_1_2_3):
        assert pila_1_2_3.desapilar() == 3
        assert pila_1_2_3.desapilar() == 2
        assert pila_1_2_3.desapilar() == 1
        assert pila_1_2_3.esta_vacia() is True

    def test_apilar_despues_de_desapilar(self, pila_1_2_3):
        pila_1_2_3.desapilar()
        pila_1_2_3.apilar(9)
        assert pila_1_2_3.tope() == 9
        assert len(pila_1_2_3) == 3


class TestHistorialEIteracion:
    def test_historial_del_mas_antiguo_al_mas_nuevo(self, pila_1_2_3):
        assert pila_1_2_3.historial() == (1, 2, 3)

    def test_historial_es_tupla(self, pila_1_2_3):
        assert isinstance(pila_1_2_3.historial(), tuple)

    def test_iterar_del_tope_hacia_abajo(self, pila_1_2_3):
        assert list(pila_1_2_3) == [3, 2, 1]

    def test_filter_sobre_pila(self, pila_1_2_3):
        assert list(filter(lambda x: x > 1, pila_1_2_3)) == [3, 2]


class TestTipoPila:
    def test_tipo_indicado_rechaza_otro_tipo(self):
        pila = Pila(int)
        with pytest.raises(DatosInvalidosError):
            pila.apilar("x")

    def test_repr(self, pila_1_2_3):
        assert repr(pila_1_2_3) == "Pila(tamanio=3)"
