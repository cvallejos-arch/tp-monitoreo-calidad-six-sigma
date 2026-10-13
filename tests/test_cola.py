"""Tests de Cola (FIFO): el primero en entrar es el primero en salir."""
import pytest

from classes.cola import Cola
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


@pytest.fixture
def cola_1_2_3():
    """Cola donde se encolaron 1, 2 y 3 (frente = 1)."""
    cola = Cola()
    cola.encolar(1)
    cola.encolar(2)
    cola.encolar(3)
    return cola


class TestColaVacia:
    def test_nueva_cola_esta_vacia(self):
        cola = Cola()
        assert cola.esta_vacia() is True
        assert len(cola) == 0

    def test_desencolar_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Cola().desencolar()

    def test_frente_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Cola().frente()


class TestOrdenFIFO:
    def test_frente_es_el_primero_encolado(self, cola_1_2_3):
        assert cola_1_2_3.frente() == 1

    def test_frente_no_elimina(self, cola_1_2_3):
        cola_1_2_3.frente()
        assert len(cola_1_2_3) == 3

    def test_desencolar_en_orden_de_llegada(self, cola_1_2_3):
        assert cola_1_2_3.desencolar() == 1
        assert cola_1_2_3.desencolar() == 2
        assert cola_1_2_3.desencolar() == 3
        assert cola_1_2_3.esta_vacia() is True

    def test_encolar_despues_de_vaciar(self, cola_1_2_3):
        """Al vaciarse, el fin se reinicia y la cola vuelve a funcionar."""
        cola_1_2_3.desencolar()
        cola_1_2_3.desencolar()
        cola_1_2_3.desencolar()
        cola_1_2_3.encolar(7)
        cola_1_2_3.encolar(8)
        assert cola_1_2_3.desencolar() == 7
        assert cola_1_2_3.frente() == 8


class TestIteracionCola:
    def test_iterar_del_frente_al_final(self, cola_1_2_3):
        assert list(cola_1_2_3) == [1, 2, 3]

    def test_map_sobre_cola(self, cola_1_2_3):
        assert list(map(lambda x: x * 10, cola_1_2_3)) == [10, 20, 30]


class TestTipoCola:
    def test_tipo_indicado_rechaza_otro_tipo(self):
        cola = Cola(int)
        with pytest.raises(DatosInvalidosError):
            cola.encolar("x")

    def test_repr(self, cola_1_2_3):
        assert repr(cola_1_2_3) == "Cola(tamanio=3)"
