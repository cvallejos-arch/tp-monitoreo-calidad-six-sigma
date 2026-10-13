"""Tests de ListaEnlazada: inserción, consulta, eliminación, regla de tipo único
y protocolos de Python (len, iter) que habilitan map, filter y sum."""
import pytest

from classes.lista_enlazada import ListaEnlazada
from classes.excepciones import DatosInvalidosError


@pytest.fixture
def lista_9_5_2():
    """Lista con los datos 9 -> 5 -> 2."""
    lista = ListaEnlazada()
    lista.insertar_final(9)
    lista.insertar_final(5)
    lista.insertar_final(2)
    return lista


class TestListaVacia:
    def test_nueva_lista_esta_vacia(self):
        lista = ListaEnlazada()
        assert lista.esta_vacia() is True
        assert len(lista) == 0

    def test_str_lista_vacia(self):
        assert str(ListaEnlazada()) == "Lista vacía"

    def test_primero_en_lista_vacia_falla(self):
        with pytest.raises(IndexError):
            ListaEnlazada().primero()

    def test_ultimo_en_lista_vacia_falla(self):
        with pytest.raises(IndexError):
            ListaEnlazada().ultimo()

    def test_eliminar_inicio_en_lista_vacia_falla(self):
        with pytest.raises(IndexError):
            ListaEnlazada().eliminar_inicio()

    def test_eliminar_en_lista_vacia_retorna_false(self):
        assert ListaEnlazada().eliminar(1) is False


class TestInsercion:
    def test_insertar_inicio_invierte_el_orden(self):
        lista = ListaEnlazada()
        lista.insertar_inicio(2)
        lista.insertar_inicio(5)
        lista.insertar_inicio(9)
        assert str(lista) == "9 -> 5 -> 2"

    def test_insertar_final_mantiene_el_orden(self, lista_9_5_2):
        assert str(lista_9_5_2) == "9 -> 5 -> 2"

    def test_primero_y_ultimo(self, lista_9_5_2):
        assert lista_9_5_2.primero() == 9
        assert lista_9_5_2.ultimo() == 2

    def test_insertar_inicio_en_vacia_actualiza_fin(self):
        lista = ListaEnlazada()
        lista.insertar_inicio(7)
        assert lista.primero() == 7
        assert lista.ultimo() == 7

    def test_insertar_actualiza_tamanio(self, lista_9_5_2):
        assert len(lista_9_5_2) == 3
        assert lista_9_5_2.esta_vacia() is False


class TestTipoUnico:
    def test_tipo_se_fija_con_el_primer_dato(self):
        lista = ListaEnlazada()
        lista.insertar_final(1)
        assert lista.tipo is int

    def test_dato_de_otro_tipo_rechazado(self, lista_9_5_2):
        with pytest.raises(DatosInvalidosError):
            lista_9_5_2.insertar_final("x")

    def test_dato_rechazado_no_se_agrega(self, lista_9_5_2):
        with pytest.raises(DatosInvalidosError):
            lista_9_5_2.insertar_inicio("x")
        assert len(lista_9_5_2) == 3

    def test_tipo_indicado_en_constructor(self):
        lista = ListaEnlazada(tipo=str)
        with pytest.raises(DatosInvalidosError):
            lista.insertar_final(1)

    def test_tipo_indicado_acepta_subclases(self):
        class Base:
            pass

        class Hija(Base):
            pass

        lista = ListaEnlazada(tipo=Base)
        lista.insertar_final(Hija())
        assert len(lista) == 1

    def test_tipo_invalido_en_constructor(self):
        with pytest.raises(DatosInvalidosError):
            ListaEnlazada(tipo="int")


class TestBuscar:
    def test_buscar_existente_retorna_nodo(self, lista_9_5_2):
        nodo = lista_9_5_2.buscar(5)
        assert nodo is not None
        assert nodo.get_dato() == 5

    def test_buscar_inexistente_retorna_none(self, lista_9_5_2):
        assert lista_9_5_2.buscar(100) is None


class TestEliminar:
    def test_eliminar_inicio_retorna_dato(self, lista_9_5_2):
        assert lista_9_5_2.eliminar_inicio() == 9
        assert str(lista_9_5_2) == "5 -> 2"
        assert len(lista_9_5_2) == 2

    def test_eliminar_inicio_hasta_vaciar(self, lista_9_5_2):
        lista_9_5_2.eliminar_inicio()
        lista_9_5_2.eliminar_inicio()
        lista_9_5_2.eliminar_inicio()
        assert lista_9_5_2.esta_vacia() is True
        with pytest.raises(IndexError):
            lista_9_5_2.ultimo()

    def test_eliminar_primer_nodo(self, lista_9_5_2):
        assert lista_9_5_2.eliminar(9) is True
        assert str(lista_9_5_2) == "5 -> 2"

    def test_eliminar_nodo_intermedio(self, lista_9_5_2):
        assert lista_9_5_2.eliminar(5) is True
        assert str(lista_9_5_2) == "9 -> 2"

    def test_eliminar_ultimo_nodo_actualiza_fin(self, lista_9_5_2):
        assert lista_9_5_2.eliminar(2) is True
        assert lista_9_5_2.ultimo() == 5
        # Insertar al final despues de borrar el ultimo debe enlazar bien
        lista_9_5_2.insertar_final(8)
        assert str(lista_9_5_2) == "9 -> 5 -> 8"

    def test_eliminar_inexistente_retorna_false(self, lista_9_5_2):
        assert lista_9_5_2.eliminar(100) is False
        assert len(lista_9_5_2) == 3

    def test_eliminar_actualiza_tamanio(self, lista_9_5_2):
        lista_9_5_2.eliminar(5)
        assert len(lista_9_5_2) == 2


class TestProtocolosPython:
    def test_for_recorre_en_orden(self, lista_9_5_2):
        recorridos = []
        for dato in lista_9_5_2:
            recorridos.append(dato)
        assert recorridos == [9, 5, 2]

    def test_list_convierte_la_lista(self, lista_9_5_2):
        assert list(lista_9_5_2) == [9, 5, 2]

    def test_sum(self, lista_9_5_2):
        assert sum(lista_9_5_2) == 16

    def test_map_con_lambda(self, lista_9_5_2):
        assert list(map(lambda x: x * 2, lista_9_5_2)) == [18, 10, 4]

    def test_filter_con_lambda(self, lista_9_5_2):
        assert list(filter(lambda x: x > 4, lista_9_5_2)) == [9, 5]

    def test_se_puede_recorrer_dos_veces(self, lista_9_5_2):
        """Cada for crea un recorrido nuevo (yield), no se agota."""
        assert list(lista_9_5_2) == list(lista_9_5_2)

    def test_repr(self, lista_9_5_2):
        assert repr(lista_9_5_2) == "ListaEnlazada(tipo=int, tamanio=3)"
