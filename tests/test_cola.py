"""Tests de Cola (FIFO): el primero en entrar es el primero en salir.
Operaciones de la materia: put, get, qsize, empty, full (y front para consultar)."""
import pytest

from classes.cola import Cola
from classes.excepciones import (
    EstructuraVaciaError,
    EstructuraLlenaError,
    DatosInvalidosError,
)


@pytest.fixture
def cola_1_2_3():
    """Cola donde se hizo put de 1, 2 y 3 (front = 1)."""
    cola = Cola()
    cola.put(1)
    cola.put(2)
    cola.put(3)
    return cola


class TestColaVacia:
    def test_nueva_cola_esta_vacia(self):
        cola = Cola()
        assert cola.empty() is True
        assert cola.qsize() == 0
        assert len(cola) == 0

    def test_get_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Cola().get()

    def test_front_vacia_falla(self):
        with pytest.raises(EstructuraVaciaError):
            Cola().front()


class TestOrdenFIFO:
    def test_front_es_el_primero_agregado(self, cola_1_2_3):
        assert cola_1_2_3.front() == 1

    def test_front_no_elimina(self, cola_1_2_3):
        cola_1_2_3.front()
        assert cola_1_2_3.qsize() == 3

    def test_get_en_orden_de_llegada(self, cola_1_2_3):
        assert cola_1_2_3.get() == 1
        assert cola_1_2_3.get() == 2
        assert cola_1_2_3.get() == 3
        assert cola_1_2_3.empty() is True

    def test_put_despues_de_vaciar(self, cola_1_2_3):
        """Al vaciarse, el fin se reinicia y la cola vuelve a funcionar."""
        cola_1_2_3.get()
        cola_1_2_3.get()
        cola_1_2_3.get()
        cola_1_2_3.put(7)
        cola_1_2_3.put(8)
        assert cola_1_2_3.get() == 7
        assert cola_1_2_3.front() == 8

    def test_qsize_y_len_coinciden(self, cola_1_2_3):
        assert cola_1_2_3.qsize() == len(cola_1_2_3) == 3


class TestCapacidad:
    def test_cola_dinamica_nunca_esta_llena(self, cola_1_2_3):
        assert cola_1_2_3.full() is False

    def test_full_al_alcanzar_maxsize(self):
        cola = Cola(maxsize=2)
        cola.put(1)
        assert cola.full() is False
        cola.put(2)
        assert cola.full() is True

    def test_put_en_cola_llena_falla(self):
        cola = Cola(maxsize=1)
        cola.put(1)
        with pytest.raises(EstructuraLlenaError):
            cola.put(2)
        assert cola.qsize() == 1

    def test_get_libera_lugar(self):
        cola = Cola(maxsize=1)
        cola.put(1)
        cola.get()
        assert cola.full() is False
        cola.put(2)
        assert cola.front() == 2

    @pytest.mark.parametrize("maxsize", [0, -1, 1.5, "3"])
    def test_maxsize_invalido(self, maxsize):
        with pytest.raises(DatosInvalidosError):
            Cola(maxsize=maxsize)


class TestIteracionCola:
    def test_iterar_del_front_al_rear(self, cola_1_2_3):
        assert list(cola_1_2_3) == [1, 2, 3]

    def test_map_sobre_cola(self, cola_1_2_3):
        assert list(map(lambda x: x * 10, cola_1_2_3)) == [10, 20, 30]


class TestTipoCola:
    def test_tipo_indicado_rechaza_otro_tipo(self):
        cola = Cola(int)
        with pytest.raises(DatosInvalidosError):
            cola.put("x")

    def test_repr(self, cola_1_2_3):
        assert repr(cola_1_2_3) == "Cola(qsize=3, maxsize=None)"
