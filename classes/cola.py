from classes.lista_enlazada import ListaEnlazada
from classes.excepciones import EstructuraVaciaError, EstructuraLlenaError, DatosInvalidosError


class Cola:
    """FIFO (first in, first out): el primer elemento agregado es el primero en salir.
    Se agrega por el extremo trasero (rear/back) y se elimina por el extremo
    frontal (front). Compone una ListaEnlazada: su `fin` permite agregar sin recorrer.
    Si se indica maxsize, la cola tiene capacidad máxima; si no, es dinámica."""

    def __init__(self, tipo=None, maxsize=None):
        if maxsize is not None and (not isinstance(maxsize, int) or maxsize <= 0):
            raise DatosInvalidosError(
                f"La capacidad máxima debe ser un entero positivo, recibido: {maxsize}"
            )
        self._lista = ListaEnlazada(tipo)
        self._maxsize = maxsize

    def put(self, dato):
        """Agrega un elemento en el extremo trasero (rear/back)."""
        if self.full():
            raise EstructuraLlenaError(
                f"La cola está llena (maxsize={self._maxsize})", maxsize=self._maxsize
            )
        self._lista.insertar_final(dato)

    def get(self):
        """Quita y retorna el elemento del extremo frontal (front)."""
        if self.empty():
            raise EstructuraVaciaError("La cola está vacía")
        return self._lista.eliminar_inicio()

    def front(self):
        """Retorna el elemento del extremo frontal (front) sin quitarlo."""
        if self.empty():
            raise EstructuraVaciaError("La cola está vacía")
        return self._lista.primero()

    def qsize(self):
        """Retorna la cantidad de elementos de la cola."""
        return len(self._lista)

    def empty(self):
        """Retorna True si la cola no tiene elementos."""
        return self._lista.esta_vacia()

    def full(self):
        """Retorna True si la cola alcanzó su capacidad máxima (nunca, si es dinámica)."""
        return self._maxsize is not None and self.qsize() >= self._maxsize

    def __len__(self):
        return self.qsize()

    def __iter__(self):
        return iter(self._lista)      # del front hacia el rear

    def __repr__(self):
        return f"Cola(qsize={self.qsize()}, maxsize={self._maxsize})"
