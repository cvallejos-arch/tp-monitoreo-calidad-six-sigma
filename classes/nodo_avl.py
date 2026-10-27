# Árbol: estructura jerárquica de nodos. El nodo inicial es la raíz;
# los nodos sin hijos son hojas. En un árbol binario cada nodo tiene
# como máximo 2 hijos: izquierdo y derecho.

from classes.excepciones import DatosInvalidosError


class NodoAVL:
    """Nodo de un árbol AVL. Guarda una clave de ordenamiento, la lista de datos
    que tienen esa clave, las referencias a sus dos hijos y su altura.

    A diferencia del nodo del apunte, admite claves repetidas: si se insertan
    varios datos con la misma clave (por ejemplo, varios defectos de gravedad 2),
    quedan todos en el mismo nodo en lugar de crear un nodo por cada uno."""

    def __init__(self, clave, dato):
        self._clave = clave
        self._datos = [dato]
        self._izquierdo = None
        self._derecho = None
        self._altura = 1  # una hoja tiene altura 1 (atributo clave del AVL)

    # --- Clave y datos ---

    def get_clave(self):
        return self._clave

    def get_datos(self):
        """Tupla con los datos de esta clave (no se puede modificar desde afuera)."""
        return tuple(self._datos)

    def agregar_dato(self, dato):
        """Agrega otro dato con la misma clave."""
        self._datos.append(dato)

    def copiar_contenido(self, otro):
        """Toma la clave y los datos de otro nodo. Se usa al eliminar un nodo con
        dos hijos: su lugar lo ocupa el contenido del sucesor in-orden."""
        self._clave = otro._clave
        self._datos = list(otro._datos)

    # --- Hijos ---

    def get_izquierdo(self):
        return self._izquierdo

    def set_izquierdo(self, nodo):
        if nodo is not None and not isinstance(nodo, NodoAVL):
            raise DatosInvalidosError("El hijo izquierdo debe ser un NodoAVL o None")
        self._izquierdo = nodo

    def get_derecho(self):
        return self._derecho

    def set_derecho(self, nodo):
        if nodo is not None and not isinstance(nodo, NodoAVL):
            raise DatosInvalidosError("El hijo derecho debe ser un NodoAVL o None")
        self._derecho = nodo

    def es_hoja(self):
        return self._izquierdo is None and self._derecho is None

    # --- Altura ---

    def get_altura(self):
        return self._altura

    def set_altura(self, altura):
        self._altura = altura

    def __repr__(self):
        return f"NodoAVL(clave={self._clave!r}, datos={len(self._datos)}, altura={self._altura})"
