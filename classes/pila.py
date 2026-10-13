from classes.lista_enlazada import ListaEnlazada
from classes.excepciones import EstructuraVaciaError


class Pila:
    """LIFO (last in, first out): el último elemento agregado es el primero en salir.
    Compone una ListaEnlazada y solo opera sobre su inicio, que es el extremo
    superior (top). El extremo inferior (bottom) no se accede directamente."""

    def __init__(self, tipo=None):
        self._lista = ListaEnlazada(tipo)

    def push(self, dato):
        """Agrega un elemento en el extremo superior (top)."""
        self._lista.insertar_inicio(dato)

    def pop(self):
        """Quita y retorna el elemento del extremo superior (top)."""
        if self.isEmpty():
            raise EstructuraVaciaError("La pila está vacía")
        return self._lista.eliminar_inicio()

    def peek(self):
        """Retorna el elemento del extremo superior (top) sin quitarlo."""
        if self.isEmpty():
            raise EstructuraVaciaError("La pila está vacía")
        return self._lista.primero()

    def isEmpty(self):
        """Retorna True si la pila no tiene elementos."""
        return self._lista.esta_vacia()

    def size(self):
        """Retorna la cantidad de elementos de la pila."""
        return len(self._lista)

    def historial(self):
        """Tupla ordenada del elemento más antiguo (bottom) al más nuevo (top)."""
        # La lista se recorre del tope hacia abajo, por eso se invierte.
        return tuple(reversed(list(self._lista)))

    def __len__(self):
        return self.size()

    def __iter__(self):
        return iter(self._lista)      # del top hacia el bottom

    def __repr__(self):
        return f"Pila(size={self.size()})"
