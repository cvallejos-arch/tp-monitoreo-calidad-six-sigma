from classes.nodo_arbol import NodoArbol
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


class ArbolBinarioBusqueda:
    """Árbol Binario de Búsqueda (ABB / BST).
    Estructura jerárquica donde para cada nodo:
      - Todos los elementos del subárbol izquierdo tienen clave menor.
      - Todos los elementos del subárbol derecho tienen clave mayor o igual.

    Todas las operaciones principales (inserción, búsqueda, recorridos,
    altura, mínimo, máximo y eliminación) están implementadas mediante recursión."""

    def __init__(self, permitir_duplicados=True):
        self._raiz = None
        self._tamanio = 0
        self._permitir_duplicados = permitir_duplicados

    @property
    def raiz(self):
        return self._raiz

    def esta_vacio(self):
        """Retorna True si el árbol no tiene ningún nodo."""
        return self._raiz is None

    # --- Inserción recursiva ---

    def insertar(self, dato, clave=None):
        """Inserta un nuevo dato en el árbol con una clave de ordenamiento.
        Si clave es None, se usa el dato como clave."""
        clave_real = dato if clave is None else clave
        nuevo_nodo = NodoArbol(dato, clave_real)
        self._raiz = self._insertar_rec(self._raiz, nuevo_nodo)
        self._tamanio += 1

    def _insertar_rec(self, actual, nuevo):
        """Caso base: actual es None -> el nuevo nodo ocupa esta posición.
        Caso recursivo: descender a izquierda o derecha según la clave."""
        if actual is None:
            return nuevo

        if nuevo.get_clave() < actual.get_clave():
            actual.set_izquierdo(self._insertar_rec(actual.get_izquierdo(), nuevo))
        elif nuevo.get_clave() > actual.get_clave():
            actual.set_derecho(self._insertar_rec(actual.get_derecho(), nuevo))
        else:
            # Clave duplicada
            if not self._permitir_duplicados:
                # Reemplaza el dato si no se permiten duplicados
                actual.set_dato(nuevo.get_dato())
                self._tamanio -= 1  # Compensa el incremento en insertar()
            else:
                # En caso de claves iguales con duplicados permitidos, se ubica a la derecha
                actual.set_derecho(self._insertar_rec(actual.get_derecho(), nuevo))

        return actual

    # --- Búsqueda recursiva ---

    def buscar(self, clave):
        """Busca recursivamente y retorna el primer dato cuya clave coincida, o None."""
        nodo = self._buscar_rec(self._raiz, clave)
        return nodo.get_dato() if nodo is not None else None

    def _buscar_rec(self, actual, clave):
        """Caso base 1: actual es None -> no encontrado.
        Caso base 2: actual.clave == clave -> encontrado.
        Caso recursivo: descender por izquierda o derecha."""
        if actual is None or actual.get_clave() == clave:
            return actual
        if clave < actual.get_clave():
            return self._buscar_rec(actual.get_izquierdo(), clave)
        return self._buscar_rec(actual.get_derecho(), clave)

    def contiene(self, clave):
        """Retorna True si existe al menos un elemento con esa clave."""
        return self._buscar_rec(self._raiz, clave) is not None

    def buscar_todos(self, clave):
        """Retorna una lista con todos los datos que poseen la clave indicada (recursivo)."""
        resultados = []
        self._buscar_todos_rec(self._raiz, clave, resultados)
        return resultados

    def _buscar_todos_rec(self, actual, clave, resultados):
        """Caso base: actual es None.
        Recorre y acumula todos los nodos que coinciden con la clave."""
        if actual is None:
            return
        if actual.get_clave() == clave:
            resultados.append(actual.get_dato())
        if clave <= actual.get_clave():
            self._buscar_todos_rec(actual.get_izquierdo(), clave, resultados)
        if clave >= actual.get_clave():
            self._buscar_todos_rec(actual.get_derecho(), clave, resultados)

    # --- Altura recursiva ---

    def altura(self):
        """Calcula la altura del árbol de forma recursiva.
        Un árbol vacío tiene altura 0; un árbol de un único nodo tiene altura 1."""
        return self._altura_rec(self._raiz)

    def _altura_rec(self, actual):
        """Caso base: nodo es None -> 0.
        Caso recursivo: 1 + max(altura_izq, altura_der)."""
        if actual is None:
            return 0
        return 1 + max(
            self._altura_rec(actual.get_izquierdo()),
            self._altura_rec(actual.get_derecho())
        )

    # --- Recorridos recursivos ---

    def recorrido_in_orden(self):
        """Recorrido In-Orden recursivo (Izquierda - Raíz - Derecha).
        Retorna los datos en orden ascendente según su clave."""
        resultado = []
        self._in_orden_rec(self._raiz, resultado)
        return resultado

    def _in_orden_rec(self, actual, resultado):
        if actual is not None:
            self._in_orden_rec(actual.get_izquierdo(), resultado)
            resultado.append(actual.get_dato())
            self._in_orden_rec(actual.get_derecho(), resultado)

    def recorrido_pre_orden(self):
        """Recorrido Pre-Orden recursivo (Raíz - Izquierda - Derecha)."""
        resultado = []
        self._pre_orden_rec(self._raiz, resultado)
        return resultado

    def _pre_orden_rec(self, actual, resultado):
        if actual is not None:
            resultado.append(actual.get_dato())
            self._pre_orden_rec(actual.get_izquierdo(), resultado)
            self._pre_orden_rec(actual.get_derecho(), resultado)

    def recorrido_post_orden(self):
        """Recorrido Post-Orden recursivo (Izquierda - Derecha - Raíz)."""
        resultado = []
        self._post_orden_rec(self._raiz, resultado)
        return resultado

    def _post_orden_rec(self, actual, resultado):
        if actual is not None:
            self._post_orden_rec(actual.get_izquierdo(), resultado)
            self._post_orden_rec(actual.get_derecho(), resultado)
            resultado.append(actual.get_dato())

    # --- Mínimo y Máximo recursivos ---

    def minimo(self):
        """Retorna el dato con la clave mínima (nodo más a la izquierda)."""
        if self.esta_vacio():
            raise EstructuraVaciaError("El árbol está vacío")
        return self._minimo_nodo(self._raiz).get_dato()

    def _minimo_nodo(self, actual):
        """Caso base: no hay hijo izquierdo -> este es el mínimo.
        Caso recursivo: descender por la izquierda."""
        if actual.get_izquierdo() is None:
            return actual
        return self._minimo_nodo(actual.get_izquierdo())

    def maximo(self):
        """Retorna el dato con la clave máxima (nodo más a la derecha)."""
        if self.esta_vacio():
            raise EstructuraVaciaError("El árbol está vacío")
        return self._maximo_nodo(self._raiz).get_dato()

    def _maximo_nodo(self, actual):
        """Caso base: no hay hijo derecho -> este es el máximo.
        Caso recursivo: descender por la derecha."""
        if actual.get_derecho() is None:
            return actual
        return self._maximo_nodo(actual.get_derecho())

    # --- Eliminación recursiva ---

    def eliminar(self, clave):
        """Elimina recursivamente el primer nodo con la clave especificada.
        Retorna True si lo eliminó, False si la clave no existía."""
        if not self.contiene(clave):
            return False
        self._raiz = self._eliminar_rec(self._raiz, clave)
        self._tamanio -= 1
        return True

    def _eliminar_rec(self, actual, clave):
        """Elimina un nodo por clave de forma recursiva contemplando los 3 casos:
        1. Nodo hoja (0 hijos)
        2. Nodo con 1 hijo
        3. Nodo con 2 hijos (reemplazo por sucesor in-order: mínimo del subárbol derecho)."""
        if actual is None:
            return None

        if clave < actual.get_clave():
            actual.set_izquierdo(self._eliminar_rec(actual.get_izquierdo(), clave))
        elif clave > actual.get_clave():
            actual.set_derecho(self._eliminar_rec(actual.get_derecho(), clave))
        else:
            # Caso encontrado: actual es el nodo a eliminar
            # Caso 1 y 2: 0 o 1 hijo
            if actual.get_izquierdo() is None:
                return actual.get_derecho()
            if actual.get_derecho() is None:
                return actual.get_izquierdo()

            # Caso 3: 2 hijos
            # Encontrar el sucesor in-order (mínimo del subárbol derecho)
            sucesor = self._minimo_nodo(actual.get_derecho())
            # Copiar clave y dato del sucesor al nodo actual
            actual.set_clave(sucesor.get_clave())
            actual.set_dato(sucesor.get_dato())
            # Eliminar recursivamente el sucesor en el subárbol derecho
            actual.set_derecho(self._eliminar_rec(actual.get_derecho(), sucesor.get_clave()))
            return actual

        return actual

    # --- Protocolos de Python ---

    def __len__(self):
        return self._tamanio

    def __iter__(self):
        """Itera los elementos en orden ascendente (in-orden)."""
        return iter(self.recorrido_in_orden())

    def __repr__(self):
        return f"ArbolBinarioBusqueda(size={self._tamanio}, altura={self.altura()})"
