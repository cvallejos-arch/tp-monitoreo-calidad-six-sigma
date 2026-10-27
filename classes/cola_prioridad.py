from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


class ColaPrioridad:
    """Cola de prioridad implementada como max-heap binario (implementación iterativa).
    Siempre sale primero el elemento de MAYOR prioridad, no el que llegó antes.
    Ejemplo de la cátedra: en una sala de urgencias se atiende primero al más grave.

    Almacenamiento: una lista en orden BFS (nivel por nivel, de izquierda a derecha).
    El árbol no tiene nodos ni referencias: su forma queda implícita en los índices.
        padre(i) = (i - 1) // 2     hijo_izq(i) = 2i + 1     hijo_der(i) = 2i + 2

    Invariantes (se cumplen siempre):
    - Forma: la lista representa un árbol binario COMPLETO -> altura = log2(n).
    - Orden: cada padre tiene prioridad mayor o igual que sus hijos -> el máximo
      está siempre en el índice 0.

    Con prioridades iguales sale primero el que llegó antes (se guarda un número
    de orden de llegada). La prioridad puede ser un número o una tupla: las tuplas
    se comparan elemento a elemento, así que (5, 8) > (5, 6) > (4, 9)."""

    def __init__(self):
        self._datos = []        # lista de dicts {valor, prioridad, orden}; índice 0 = máximo
        self._llegadas = 0      # contador de llegadas, para desempatar

    # ============================================================
    #  Capa 1: navegación por índice
    # ============================================================

    def padre(self, i):
        """Índice del padre de i, o None si i es la raíz."""
        return (i - 1) // 2 if i > 0 else None

    def hijo_izq(self, i):
        """Índice del hijo izquierdo de i, o None si no existe."""
        indice = 2 * i + 1
        return indice if indice < len(self._datos) else None

    def hijo_der(self, i):
        """Índice del hijo derecho de i, o None si no existe."""
        indice = 2 * i + 2
        return indice if indice < len(self._datos) else None

    # ============================================================
    #  Capa 2: intercambio y comparación
    # ============================================================

    def intercambiar(self, i, j):
        """Intercambia los elementos de las posiciones i y j. Solo se mueven los
        datos: la forma del árbol (quién es hijo de quién) está en los índices."""
        self._datos[i], self._datos[j] = self._datos[j], self._datos[i]

    def _es_mayor(self, i, j):
        """True si el elemento i tiene que salir antes que el j: mayor prioridad,
        o la misma prioridad y llegó antes."""
        a, b = self._datos[i], self._datos[j]
        if a["prioridad"] != b["prioridad"]:
            return a["prioridad"] > b["prioridad"]
        return a["orden"] < b["orden"]

    # ============================================================
    #  Capa 3: reordenamiento
    # ============================================================

    def _subir(self, i):
        """Después de insertar: el elemento nuevo sube mientras sea mayor que su
        padre. Como mucho un intercambio por nivel -> O(log n)."""
        while self.padre(i) is not None:
            p = self.padre(i)
            if not self._es_mayor(i, p):
                break                   # el padre ya es mayor: invariante restaurado
            self.intercambiar(i, p)
            i = p                       # seguimos desde la posición del padre

    def _bajar(self, i):
        """Después de extraer: el elemento que quedó en la raíz baja mientras algún
        hijo sea mayor, siempre por el hijo MAYOR. Como mucho un intercambio por
        nivel -> O(log n)."""
        while True:
            izquierdo = self.hijo_izq(i)
            derecho = self.hijo_der(i)
            mayor = i                   # suponemos que i es el mayor de los tres

            if izquierdo is not None and self._es_mayor(izquierdo, mayor):
                mayor = izquierdo
            if derecho is not None and self._es_mayor(derecho, mayor):
                mayor = derecho

            if mayor == i:
                break                   # ningún hijo es mayor: invariante restaurado
            self.intercambiar(i, mayor)
            i = mayor                   # seguimos desde donde quedó el dato

    # ============================================================
    #  Capa 4: interfaz pública
    # ============================================================

    def insertar(self, valor, prioridad):
        """Agrega un elemento. O(log n).
        1. Se agrega al final de la lista -> el árbol sigue completo.
        2. _subir desde el último índice -> se restaura el orden."""
        if not isinstance(prioridad, (int, float, tuple)) or isinstance(prioridad, bool):
            raise DatosInvalidosError(
                f"La prioridad tiene que ser un número o una tupla, recibido: {prioridad!r}"
            )
        self._datos.append({"valor": valor, "prioridad": prioridad, "orden": self._llegadas})
        self._llegadas += 1
        self._subir(len(self._datos) - 1)

    def extraer_maximo(self):
        """Quita y retorna el valor de mayor prioridad. O(log n).
        1. Se intercambia la raíz (el máximo) con el último elemento.
        2. Se quita el último (pop) -> el árbol sigue completo.
        3. _bajar desde la raíz -> se restaura el orden."""
        if self.esta_vacia():
            raise EstructuraVaciaError("La cola de prioridad está vacía")
        self.intercambiar(0, len(self._datos) - 1)
        maximo = self._datos.pop()
        if self._datos:
            self._bajar(0)
        return maximo["valor"]

    def ver_maximo(self):
        """Retorna el valor de mayor prioridad sin quitarlo. O(1): está en el índice 0."""
        if self.esta_vacia():
            raise EstructuraVaciaError("La cola de prioridad está vacía")
        return self._datos[0]["valor"]

    def prioridad_maxima(self):
        """Retorna la prioridad del elemento que sale primero, sin quitarlo."""
        if self.esta_vacia():
            raise EstructuraVaciaError("La cola de prioridad está vacía")
        return self._datos[0]["prioridad"]

    def en_orden_de_prioridad(self):
        """Lista de valores en el orden en que saldrían, SIN vaciar la cola:
        se extraen de una copia."""
        copia = ColaPrioridad()
        copia._datos = list(self._datos)
        copia._llegadas = self._llegadas
        orden = []
        while copia:
            orden.append(copia.extraer_maximo())
        return orden

    def esta_vacia(self):
        return not self._datos

    def __len__(self):
        return len(self._datos)

    def __bool__(self):
        """Permite escribir `while cola:` (True si tiene elementos)."""
        return bool(self._datos)

    def __repr__(self):
        return f"ColaPrioridad(tamanio={len(self._datos)})"
