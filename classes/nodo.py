# Lista simplemente enlazada: la referencia es unidireccional
# doblemente enlazada: entre cada par de nodos existen dos referencias, del primero al siguiente y viceversa.
# ciclo: no hay ultimo nodo, todos tienen referencia.

# inicio: ref al primer nodo
# siguiente: ref al nodo que sigue
# None: no existe otro nodo despues

# regla de la materia: los nodos de una misma lista almacenan datos del mismo tipo.

from classes.excepciones import DatosInvalidosError


class Nodo:
    def __init__(self, dato):
        self._dato = dato
        self._siguiente = None

    def get_dato(self):
        return self._dato

    def get_siguiente(self):
        return self._siguiente

    def set_dato(self, nuevo_dato):
        """Reemplaza el dato del nodo. El nuevo dato debe ser del mismo tipo que el actual."""
        if type(self._dato) != type(nuevo_dato):
            raise DatosInvalidosError(
                f"El nuevo dato debe ser de tipo '{type(self._dato).__name__}', "
                f"recibido: '{type(nuevo_dato).__name__}'"
            )
        self._dato = nuevo_dato

    def set_siguiente(self, nuevo_siguiente):
        """Enlaza este nodo con el siguiente. Debe ser un Nodo o None (fin de la lista)."""
        if nuevo_siguiente is not None and not isinstance(nuevo_siguiente, Nodo):
            raise DatosInvalidosError("El siguiente debe ser un Nodo o None")
        self._siguiente = nuevo_siguiente

    def __str__(self):
        return f"{self._dato}"

    def __repr__(self):
        return f"Nodo(dato={self._dato!r})"
