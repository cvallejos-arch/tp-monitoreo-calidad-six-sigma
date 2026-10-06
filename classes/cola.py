from classes.lista_enlazada import ListaEnlazada
from classes.excepciones import EstructuraVaciaError


class Cola:
    """FIFO. Encola al final (O(1) gracias a `fin`) y desencola del inicio."""

    def __init__(self, tipo=None):
        self._lista = ListaEnlazada(tipo)

    def encolar(self, dato):
        self._lista.insertar_final(dato)

    def desencolar(self):
        if self.esta_vacia():
            raise EstructuraVaciaError("La cola está vacía")
        return self._lista.eliminar_inicio()

    def frente(self):
        if self.esta_vacia():
            raise EstructuraVaciaError("La cola está vacía")
        return self._lista.primero()

    def esta_vacia(self):
        return self._lista.esta_vacia()

    def __len__(self):
        return len(self._lista)

    def __iter__(self):
        return iter(self._lista)      # del frente hacia el final

    def __repr__(self):
        return f"Cola(tamanio={len(self)})"