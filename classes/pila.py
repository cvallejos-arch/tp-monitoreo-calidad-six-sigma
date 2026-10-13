from classes.lista_enlazada import ListaEnlazada
from classes.excepciones import EstructuraVaciaError


class Pila:
    """LIFO. Compone una ListaEnlazada y solo opera sobre su inicio."""

    def __init__(self, tipo=None):
        self._lista = ListaEnlazada(tipo)

    def apilar(self, dato):
        self._lista.insertar_inicio(dato)

    def desapilar(self):
        if self.esta_vacia():
            raise EstructuraVaciaError("La pila está vacía")
        return self._lista.eliminar_inicio()

    def tope(self):
        if self.esta_vacia():
            raise EstructuraVaciaError("La pila está vacía")
        return self._lista.primero()

    def esta_vacia(self):
        return self._lista.esta_vacia()

    def historial(self):
        """Tupla ordenada del elemento más antiguo al más nuevo (copia inmutable)."""
        elementos = []
        for dato in self._lista:      # itera del tope hacia abajo
            elementos.insert(0, dato)
        return tuple(elementos)

    def __len__(self):
        return len(self._lista)

    def __iter__(self):
        return iter(self._lista)      # del tope hacia abajo

    def __repr__(self):
        return f"Pila(tamanio={len(self)})"