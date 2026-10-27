from classes.excepciones import DatosInvalidosError


class NodoArbol:
    """Nodo para Árbol Binario de Búsqueda (ABB).
    Contiene un dato, una clave de ordenamiento y referencias
    a sus subárboles izquierdo y derecho."""

    def __init__(self, dato, clave=None):
        self._dato = dato
        # Si no se especifica clave, el propio dato actúa como clave de ordenamiento.
        self._clave = dato if clave is None else clave
        self._izquierdo = None
        self._derecho = None

    def get_dato(self):
        return self._dato

    def set_dato(self, nuevo_dato):
        self._dato = nuevo_dato

    def get_clave(self):
        return self._clave

    def set_clave(self, nueva_clave):
        self._clave = nueva_clave

    def get_izquierdo(self):
        return self._izquierdo

    def set_izquierdo(self, nodo):
        if nodo is not None and not isinstance(nodo, NodoArbol):
            raise DatosInvalidosError("El hijo izquierdo debe ser un NodoArbol o None")
        self._izquierdo = nodo

    def get_derecho(self):
        return self._derecho

    def set_derecho(self, nodo):
        if nodo is not None and not isinstance(nodo, NodoArbol):
            raise DatosInvalidosError("El hijo derecho debe ser un NodoArbol o None")
        self._derecho = nodo

    def es_hoja(self):
        """Retorna True si el nodo no tiene descendientes."""
        return self._izquierdo is None and self._derecho is None

    def cantidad_hijos(self):
        """Retorna la cantidad de hijos no nulos (0, 1 o 2)."""
        hijos = 0
        if self._izquierdo is not None:
            hijos += 1
        if self._derecho is not None:
            hijos += 1
        return hijos

    def __repr__(self):
        return f"NodoArbol(clave={self._clave!r}, dato={self._dato!r})"
