from classes.nodo_avl import NodoAVL
from classes.cola import Cola
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError


class ArbolAVL:
    """Árbol AVL (Adelson-Velsky y Landis, 1962): un árbol binario de búsqueda
    que se rebalancea solo después de cada inserción o eliminación.

    Regla de búsqueda: claves menores a la izquierda, mayores a la derecha.
    Regla de balance: en cada nodo, factor de balance = altura(izquierdo) - altura(derecho)
    tiene que ser -1, 0 o 1. Si da 2 o -2, se corrige con rotaciones.

    Así la altura queda siempre del orden de log2(n), y buscar, insertar y eliminar
    son O(log n) garantizado. Un árbol binario de búsqueda sin balance, en cambio,
    se degenera en una lista si los datos llegan ordenados, y buscar pasa a ser O(n).

    Las operaciones son recursivas (caso base + caso recursivo). Los 4 pasos del AVL:
    1. Insertar/eliminar como en un árbol de búsqueda común, recursivamente.
    2. Al volver de la recursión, actualizar la altura de cada nodo.
    3. Calcular su factor de balance.
    4. Si está desbalanceado, rotar."""

    def __init__(self):
        self._raiz = None
        self._tamanio = 0   # cantidad de datos (puede haber varios por nodo)

    @property
    def raiz(self):
        return self._raiz

    def esta_vacio(self):
        return self._raiz is None

    # ============================================================
    #  ALTURA, BALANCE Y ROTACIONES
    # ============================================================

    def _altura_nodo(self, nodo):
        """Altura guardada en el nodo. Un subárbol vacío (None) tiene altura 0."""
        return nodo.get_altura() if nodo is not None else 0

    def _actualizar_altura(self, nodo):
        nodo.set_altura(1 + max(self._altura_nodo(nodo.get_izquierdo()),
                                self._altura_nodo(nodo.get_derecho())))

    def _factor_balance(self, nodo):
        """altura(izquierdo) - altura(derecho). Positivo = cargado a la izquierda."""
        if nodo is None:
            return 0
        return self._altura_nodo(nodo.get_izquierdo()) - self._altura_nodo(nodo.get_derecho())

    def _rotar_derecha(self, y):
        """Rotación simple a la derecha (corrige el caso izquierda-izquierda).

              y              x
             / \\            / \\
            x   C    ->    A   y
           / \\                / \\
          A   T2             T2  C

        x sube y pasa a ser la raíz del subárbol; T2 cambia de padre."""
        x = y.get_izquierdo()
        t2 = x.get_derecho()

        x.set_derecho(y)
        y.set_izquierdo(t2)

        self._actualizar_altura(y)   # primero y, que quedó abajo
        self._actualizar_altura(x)
        return x

    def _rotar_izquierda(self, x):
        """Rotación simple a la izquierda (corrige el caso derecha-derecha).

            x                  y
           / \\                / \\
          A   y      ->      x   C
             / \\            / \\
            T2  C          A   T2

        y sube y pasa a ser la raíz del subárbol; T2 cambia de padre."""
        y = x.get_derecho()
        t2 = y.get_izquierdo()

        y.set_izquierdo(x)
        x.set_derecho(t2)

        self._actualizar_altura(x)   # primero x, que quedó abajo
        self._actualizar_altura(y)
        return y

    def _balancear(self, nodo):
        """Pasos 2 a 4 del AVL sobre un nodo: actualiza su altura y, si quedó
        desbalanceado, aplica la rotación que corresponde. Retorna la nueva raíz
        del subárbol.

        Para elegir el caso se mira el factor de balance del hijo cargado (el apunte
        compara la clave insertada con la del hijo; es equivalente al insertar, y
        mirar el factor del hijo sirve también para eliminar)."""
        self._actualizar_altura(nodo)
        balance = self._factor_balance(nodo)

        if balance > 1:                                         # cargado a la izquierda
            if self._factor_balance(nodo.get_izquierdo()) < 0:
                # Caso izquierda-derecha: primero rotar el hijo a la izquierda
                nodo.set_izquierdo(self._rotar_izquierda(nodo.get_izquierdo()))
            # Caso izquierda-izquierda (o el LR ya convertido): rotar a la derecha
            return self._rotar_derecha(nodo)

        if balance < -1:                                        # cargado a la derecha
            if self._factor_balance(nodo.get_derecho()) > 0:
                # Caso derecha-izquierda: primero rotar el hijo a la derecha
                nodo.set_derecho(self._rotar_derecha(nodo.get_derecho()))
            # Caso derecha-derecha (o el RL ya convertido): rotar a la izquierda
            return self._rotar_izquierda(nodo)

        return nodo                                             # ya está balanceado

    # ============================================================
    #  INSERTAR
    # ============================================================

    def insertar(self, clave, dato):
        """Inserta un dato con su clave de ordenamiento. Si la clave ya existe,
        el dato se agrega a ese nodo. Las claves tienen que poder compararse
        entre sí (por ejemplo, todas números o todas fechas)."""
        if clave is None:
            raise DatosInvalidosError("La clave no puede ser None")
        try:
            self._raiz = self._insertar_rec(self._raiz, clave, dato)
        except TypeError as e:
            raise DatosInvalidosError(
                f"La clave {clave!r} no se puede comparar con las claves del árbol"
            ) from e
        self._tamanio += 1

    def _insertar_rec(self, nodo, clave, dato):
        # Caso base: lugar vacío -> el dato va en un nodo nuevo (una hoja)
        if nodo is None:
            return NodoAVL(clave, dato)

        # Caso recursivo: bajar por la izquierda o la derecha según la clave
        if clave < nodo.get_clave():
            nodo.set_izquierdo(self._insertar_rec(nodo.get_izquierdo(), clave, dato))
        elif clave > nodo.get_clave():
            nodo.set_derecho(self._insertar_rec(nodo.get_derecho(), clave, dato))
        else:
            # Clave repetida: se agrega al mismo nodo, la forma del árbol no cambia
            nodo.agregar_dato(dato)
            return nodo

        # Al volver de la recursión: actualizar altura y rotar si hace falta
        return self._balancear(nodo)

    # ============================================================
    #  BUSCAR
    # ============================================================

    def buscar(self, clave):
        """Retorna una tupla con todos los datos que tienen esa clave
        (vacía si no hay ninguno). O(log n) porque el árbol está balanceado."""
        nodo = self._buscar_rec(self._raiz, clave)
        return nodo.get_datos() if nodo is not None else ()

    def _buscar_rec(self, nodo, clave):
        # Caso base 1: llegamos a un lugar vacío -> la clave no está
        # Caso base 2: encontramos la clave
        if nodo is None or nodo.get_clave() == clave:
            return nodo
        # Caso recursivo: seguir por un solo lado (se descarta la otra mitad)
        if clave < nodo.get_clave():
            return self._buscar_rec(nodo.get_izquierdo(), clave)
        return self._buscar_rec(nodo.get_derecho(), clave)

    def contiene(self, clave):
        return self._buscar_rec(self._raiz, clave) is not None

    def buscar_rango(self, desde, hasta):
        """Retorna una lista con los datos cuya clave está entre desde y hasta
        (ambos incluidos), ordenados por clave. Solo entra a las ramas que
        pueden tener claves del rango."""
        resultado = []
        self._buscar_rango_rec(self._raiz, desde, hasta, resultado)
        return resultado

    def _buscar_rango_rec(self, nodo, desde, hasta, resultado):
        # Caso base: subárbol vacío
        if nodo is None:
            return
        clave = nodo.get_clave()
        # Caso recursivo: la izquierda solo puede aportar si la clave es mayor a 'desde'
        if clave > desde:
            self._buscar_rango_rec(nodo.get_izquierdo(), desde, hasta, resultado)
        if desde <= clave <= hasta:
            resultado.extend(nodo.get_datos())
        # La derecha solo puede aportar si la clave es menor a 'hasta'
        if clave < hasta:
            self._buscar_rango_rec(nodo.get_derecho(), desde, hasta, resultado)

    # ============================================================
    #  MÍNIMO Y MÁXIMO
    # ============================================================

    def minimo(self):
        """Datos con la clave más chica (el nodo más a la izquierda)."""
        if self.esta_vacio():
            raise EstructuraVaciaError("El árbol está vacío")
        return self._minimo_nodo(self._raiz).get_datos()

    def _minimo_nodo(self, nodo):
        # Caso base: no hay hijo izquierdo -> este es el mínimo
        if nodo.get_izquierdo() is None:
            return nodo
        # Caso recursivo: seguir bajando por la izquierda
        return self._minimo_nodo(nodo.get_izquierdo())

    def maximo(self):
        """Datos con la clave más grande (el nodo más a la derecha)."""
        if self.esta_vacio():
            raise EstructuraVaciaError("El árbol está vacío")
        return self._maximo_nodo(self._raiz).get_datos()

    def _maximo_nodo(self, nodo):
        if nodo.get_derecho() is None:
            return nodo
        return self._maximo_nodo(nodo.get_derecho())

    # ============================================================
    #  ELIMINAR
    # ============================================================

    def eliminar(self, clave):
        """Elimina la clave y todos sus datos. Retorna True si la eliminó,
        False si no existía. Después de eliminar, el árbol se rebalancea."""
        nodo = self._buscar_rec(self._raiz, clave)
        if nodo is None:
            return False
        cantidad = len(nodo.get_datos())
        self._raiz = self._eliminar_rec(self._raiz, clave)
        self._tamanio -= cantidad
        return True

    def _eliminar_rec(self, nodo, clave):
        # Caso base: subárbol vacío
        if nodo is None:
            return None

        # Caso recursivo: buscar el nodo a eliminar
        if clave < nodo.get_clave():
            nodo.set_izquierdo(self._eliminar_rec(nodo.get_izquierdo(), clave))
        elif clave > nodo.get_clave():
            nodo.set_derecho(self._eliminar_rec(nodo.get_derecho(), clave))
        else:
            # Encontrado. Casos 1 y 2: sin hijos o con un solo hijo -> lo reemplaza su hijo
            if nodo.get_izquierdo() is None:
                return nodo.get_derecho()
            if nodo.get_derecho() is None:
                return nodo.get_izquierdo()
            # Caso 3: dos hijos -> toma el contenido del sucesor in-orden
            # (el mínimo del subárbol derecho) y se elimina ese sucesor
            sucesor = self._minimo_nodo(nodo.get_derecho())
            nodo.copiar_contenido(sucesor)
            nodo.set_derecho(self._eliminar_rec(nodo.get_derecho(), sucesor.get_clave()))

        # Al volver de la recursión: actualizar altura y rotar si hace falta
        return self._balancear(nodo)

    # ============================================================
    #  RECORRIDOS
    # ============================================================

    def recorrido_in_orden(self):
        """Izquierdo -> raíz -> derecho: los datos ordenados de menor a mayor clave."""
        resultado = []
        self._in_orden_rec(self._raiz, resultado)
        return resultado

    def _in_orden_rec(self, nodo, resultado):
        if nodo is not None:
            self._in_orden_rec(nodo.get_izquierdo(), resultado)
            resultado.extend(nodo.get_datos())
            self._in_orden_rec(nodo.get_derecho(), resultado)

    def recorrido_pre_orden(self):
        """Raíz -> izquierdo -> derecho: útil para copiar el árbol."""
        resultado = []
        self._pre_orden_rec(self._raiz, resultado)
        return resultado

    def _pre_orden_rec(self, nodo, resultado):
        if nodo is not None:
            resultado.extend(nodo.get_datos())
            self._pre_orden_rec(nodo.get_izquierdo(), resultado)
            self._pre_orden_rec(nodo.get_derecho(), resultado)

    def recorrido_post_orden(self):
        """Izquierdo -> derecho -> raíz: útil para eliminar (primero los hijos)."""
        resultado = []
        self._post_orden_rec(self._raiz, resultado)
        return resultado

    def _post_orden_rec(self, nodo, resultado):
        if nodo is not None:
            self._post_orden_rec(nodo.get_izquierdo(), resultado)
            self._post_orden_rec(nodo.get_derecho(), resultado)
            resultado.extend(nodo.get_datos())

    def claves_in_orden(self):
        """Las claves (sin repetir) de menor a mayor."""
        claves = []
        self._claves_rec(self._raiz, claves)
        return claves

    def _claves_rec(self, nodo, claves):
        if nodo is not None:
            self._claves_rec(nodo.get_izquierdo(), claves)
            claves.append(nodo.get_clave())
            self._claves_rec(nodo.get_derecho(), claves)

    def niveles(self):
        """Recorrido por niveles (BFS), con nuestra Cola: una lista de claves por
        nivel, de la raíz hacia abajo. No es recursivo. Sirve para ver la forma
        del árbol, por ejemplo después de una rotación."""
        resultado = []
        if self.esta_vacio():
            return resultado
        cola = Cola(NodoAVL)
        cola.put(self._raiz)
        while not cola.empty():
            nivel = []
            for _ in range(cola.qsize()):          # los nodos de este nivel
                nodo = cola.get()
                nivel.append(nodo.get_clave())
                if nodo.get_izquierdo() is not None:
                    cola.put(nodo.get_izquierdo())
                if nodo.get_derecho() is not None:
                    cola.put(nodo.get_derecho())
            resultado.append(nivel)
        return resultado

    # ============================================================
    #  CONSULTAS DE LA FORMA DEL ÁRBOL
    # ============================================================

    def altura(self):
        """Altura del árbol: 0 si está vacío, 1 si tiene solo la raíz."""
        return self._altura_nodo(self._raiz)

    def cantidad_nodos(self):
        """Cantidad de claves distintas (un nodo por clave)."""
        return self._contar_nodos_rec(self._raiz)

    def _contar_nodos_rec(self, nodo):
        # Caso base: subárbol vacío -> 0 nodos
        if nodo is None:
            return 0
        # Caso recursivo: este nodo + los de cada lado
        return 1 + self._contar_nodos_rec(nodo.get_izquierdo()) + \
            self._contar_nodos_rec(nodo.get_derecho())

    def esta_balanceado(self):
        """Verifica en TODOS los nodos que el factor de balance sea -1, 0 o 1
        y que la altura guardada sea la correcta."""
        return self._verificar_rec(self._raiz) is not None

    def _verificar_rec(self, nodo):
        """Retorna la altura real del subárbol, o None si encuentra un problema."""
        if nodo is None:
            return 0
        altura_izq = self._verificar_rec(nodo.get_izquierdo())
        altura_der = self._verificar_rec(nodo.get_derecho())
        if altura_izq is None or altura_der is None:
            return None
        if abs(altura_izq - altura_der) > 1:
            return None
        altura_real = 1 + max(altura_izq, altura_der)
        return altura_real if altura_real == nodo.get_altura() else None

    # --- Protocolos de Python ---

    def __len__(self):
        """Cantidad de datos guardados (contando los que comparten clave)."""
        return self._tamanio

    def __iter__(self):
        """Recorre los datos de menor a mayor clave (in-orden)."""
        return iter(self.recorrido_in_orden())

    def __repr__(self):
        return (f"ArbolAVL(datos={self._tamanio}, claves={self.cantidad_nodos()}, "
                f"altura={self.altura()})")
