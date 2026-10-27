from classes.nodo import Nodo
from classes.excepciones import DatosInvalidosError


class ListaEnlazada:
    """Lista simplemente enlazada. Todos los nodos almacenan datos del mismo tipo:
    el tipo se fija en el constructor o, si no se indica, con el primer dato insertado."""

    def __init__(self, tipo=None):
        if tipo is not None and not isinstance(tipo, type):
            raise DatosInvalidosError(f"El tipo de la lista debe ser una clase, recibido: {tipo}")
        self._inicio = None
        self._fin = None  # ref al último nodo, permite insertar al final sin recorrer
        self._tamanio = 0
        self._tipo = tipo

    @property
    def tipo(self):
        return self._tipo

    def esta_vacia(self):
        return self._inicio is None

    def _validar_tipo(self, dato):
        """Aplica la regla de la materia: todos los datos deben ser del mismo tipo."""
        if self._tipo is None:
            self._tipo = type(dato)
        elif not isinstance(dato, self._tipo):
            raise DatosInvalidosError(
                f"La lista solo admite datos de tipo '{self._tipo.__name__}', "
                f"recibido: '{type(dato).__name__}'"
            )

    # Insertar

    def insertar_inicio(self, dato):
        self._validar_tipo(dato)
        nuevo = Nodo(dato)
        nuevo.set_siguiente(self._inicio)
        self._inicio = nuevo
        if self._fin is None:
            self._fin = nuevo
        self._tamanio += 1

    def insertar_final(self, dato):
        self._validar_tipo(dato)
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self._inicio = nuevo
        else:
            self._fin.set_siguiente(nuevo)
        self._fin = nuevo
        self._tamanio += 1

    # Consultas

    def primero(self):
        """Retorna el dato del primer nodo sin eliminarlo."""
        if self.esta_vacia():
            raise IndexError("La lista está vacía")
        return self._inicio.get_dato()

    def ultimo(self):
        """Retorna el dato del último nodo sin eliminarlo."""
        if self.esta_vacia():
            raise IndexError("La lista está vacía")
        return self._fin.get_dato()

    def buscar(self, valor):
        """Retorna el primer nodo cuyo dato sea igual a valor, o None si no existe."""
        actual = self._inicio
        while actual is not None:
            if actual.get_dato() == valor:
                return actual
            actual = actual.get_siguiente()
        return None

    # Eliminar

    def eliminar_inicio(self):
        """Elimina el primer nodo y retorna su dato."""
        if self.esta_vacia():
            raise IndexError("La lista está vacía")
        dato = self._inicio.get_dato()
        self._inicio = self._inicio.get_siguiente()
        if self._inicio is None:
            self._fin = None
        self._tamanio -= 1
        return dato

    def eliminar(self, valor):
        """Elimina el primer nodo cuyo dato sea igual a valor. Retorna True si lo eliminó."""
        actual = self._inicio
        anterior = None

        while actual is not None:
            if actual.get_dato() == valor:
                if anterior is None:
                    # Caso 1: eliminar el primer nodo
                    self._inicio = actual.get_siguiente()
                else:
                    # Caso 2 y 3: eliminar nodo intermedio o último
                    anterior.set_siguiente(actual.get_siguiente())

                if actual is self._fin:
                    self._fin = anterior
                self._tamanio -= 1
                return True

            anterior = actual
            actual = actual.get_siguiente()

        return False

    # --- Métodos recursivos (Unidad 7 EDP) ---

    def longitud_recursiva(self):
        """Calcula la cantidad de elementos de forma recursiva."""
        return self._longitud_nodo(self._inicio)

    def _longitud_nodo(self, nodo):
        """Caso base: nodo es None -> 0. Caso recursivo: 1 + longitud(siguiente)."""
        if nodo is None:
            return 0
        return 1 + self._longitud_nodo(nodo.get_siguiente())

    def buscar_recursivo(self, valor):
        """Retorna el primer nodo cuyo dato sea igual a valor de forma recursiva, o None."""
        return self._buscar_nodo(self._inicio, valor)

    def _buscar_nodo(self, nodo, valor):
        """Caso base 1: nodo es None -> no encontrado.
        Caso base 2: coincide el dato -> encontrado.
        Caso recursivo: buscar en nodo.siguiente."""
        if nodo is None:
            return None
        if nodo.get_dato() == valor:
            return nodo
        return self._buscar_nodo(nodo.get_siguiente(), valor)

    def contar_recursivo(self, valor):
        """Cuenta recursivamente cuántas veces aparece un valor en la lista."""
        return self._contar_nodo(self._inicio, valor)

    def _contar_nodo(self, nodo, valor):
        """Caso base: nodo es None -> 0.
        Caso recursivo: (1 si coincide else 0) + contar en siguiente."""
        if nodo is None:
            return 0
        coincide = 1 if nodo.get_dato() == valor else 0
        return coincide + self._contar_nodo(nodo.get_siguiente(), valor)

    def a_lista_recursiva(self):
        """Construye recursivamente una lista estándar de Python con los datos."""
        return self._a_lista_nodo(self._inicio)

    def _a_lista_nodo(self, nodo):
        """Caso base: nodo es None -> [].
        Caso recursivo: [nodo.dato] + lista(nodo.siguiente)."""
        if nodo is None:
            return []
        return [nodo.get_dato()] + self._a_lista_nodo(nodo.get_siguiente())

    def invertir_recursivo(self):
        """Invierte los enlaces de la lista de forma recursiva y actualiza inicio y fin."""
        if self._inicio is None or self._inicio.get_siguiente() is None:
            return
        self._fin = self._inicio
        self._inicio = self._invertir_nodo(self._inicio)

    def _invertir_nodo(self, nodo):
        """Caso base: último nodo de la lista -> pasa a ser la nueva cabeza.
        Caso recursivo: invertir el resto y apuntar el siguiente nodo hacia este."""
        if nodo is None or nodo.get_siguiente() is None:
            return nodo
        nueva_cabeza = self._invertir_nodo(nodo.get_siguiente())
        nodo.get_siguiente().set_siguiente(nodo)
        nodo.set_siguiente(None)
        return nueva_cabeza

    # Protocolos de Python 

    def __len__(self):
        return self._tamanio

    def __iter__(self):
        """Recorre la lista del inicio al fin, entregando los datos (no los nodos)."""
        actual = self._inicio
        while actual is not None:
            yield actual.get_dato()
            actual = actual.get_siguiente()

    def __str__(self):
        if self.esta_vacia():
            return "Lista vacía"
        return " -> ".join(map(str, self))

    def __repr__(self):
        tipo = self._tipo.__name__ if self._tipo is not None else None
        return f"ListaEnlazada(tipo={tipo}, tamanio={self._tamanio})"
