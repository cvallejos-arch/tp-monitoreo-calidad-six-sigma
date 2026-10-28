from classes.entidad import Entidad
from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad, validar_nombre_tecnico
from classes.excepciones import TransicionIlegalError, DatosInvalidosError
from classes.cola import Cola
from classes.arbol_avl import ArbolAVL
import uuid


class Lote(Entidad):
    # Estados en los que una muestra se considera cerrada (inspección finalizada).
    ESTADOS_FINALES = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)

    def __init__(self, nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = validar_nombre_tecnico(
            nombre_componentes,
            "nombre_componentes"
        )
        self._cantidad_fabricada = validar_cantidad(cantidad_fabricada)
        self._estado = EstadoLote.EN_PRODUCCION
        self._muestras = {}  # dict {muestra.id: muestra}
        self._pendientes = Cola(Muestra)  # cola FIFO de muestras pendientes de inspección

    @property
    def id(self):
        return self._id

    @property
    def nombre_componentes(self):
        return self._nombre_componentes

    @property
    def cantidad_fabricada(self):
        return self._cantidad_fabricada

    @property
    def estado(self):
        return self._estado

    @property
    def muestras(self):
        """Retorna una tupla inmutable de las muestras del lote."""
        return tuple(self._muestras.values())

    @property
    def capacidad_libre(self):
        """Unidades que todavía se pueden asignar a muestras nuevas."""
        return self._cantidad_fabricada - sum(map(lambda m: m.cantidad, self._muestras.values()))

    def __contains__(self, muestra):
        """Permite escribir `muestra in lote`: True si la muestra pertenece a este lote.
        Busca por id en el diccionario de muestras (O(1))."""
        return isinstance(muestra, Muestra) and muestra.id in self._muestras

    def crear_muestra(self, cantidad):
        """Crea una muestra que pertenece a este lote (composición).
        Valida que la capacidad no se exceda."""
        validar_cantidad(cantidad)

        # Transformamos cada muestra en su cantidad y luego las sumamos.
        capacidad_usada = sum(
            map(lambda m: m.cantidad, self._muestras.values())
        )

        if capacidad_usada + cantidad > self._cantidad_fabricada:
            raise TransicionIlegalError(
                f"No se puede crear una muestra de {cantidad} unidades: "
                f"la suma ({capacidad_usada + cantidad}) excede la cantidad "
                f"fabricada ({self._cantidad_fabricada}).",
                lote_id=self._id,
                capacidad_usada=capacidad_usada,
                cantidad_solicitada=cantidad,
                cantidad_fabricada=self._cantidad_fabricada
            )

        muestra = Muestra(cantidad, self._id)
        self._muestras[muestra.id] = muestra
        self._pendientes.put(muestra)  # put: agrega la muestra al final de la cola (rear)
        return muestra

    # --- Cola de pendientes ---

    def siguiente_muestra_pendiente(self):
        """Retorna la próxima muestra PENDIENTE en orden de creación, o None.
        NO la quita de la cola: sigue en el front hasta que deje de estar PENDIENTE.
        Descarta del front las muestras que ya no están pendientes (p. ej.
        inspeccionadas fuera de orden). No modifica muestras, reportes ni
        el estado del lote."""
        while not self._pendientes.empty():  # empty: True si la cola no tiene elementos
            primera = self._pendientes.front()  # front: consulta el primer elemento sin quitarlo
            if primera.estado == EstadoMuestra.PENDIENTE:
                return primera
            self._pendientes.get()  # get: quita el primer elemento de la cola (front)
        return None

    def pendientes_en_orden(self):
        """Retorna las muestras PENDIENTE en orden de creación, sin tocar la cola."""
        return tuple(
            filter(lambda m: m.estado == EstadoMuestra.PENDIENTE, self._pendientes)
        )

    # --- Decisión del lote ---

    def decidir(self):
        """Decide el estado del lote basado en el porcentaje de muestras
        no conformes. RECHAZADO si > 5%, APROBADO si <= 5%.
        La decisión es final."""
        if self._estado != EstadoLote.EN_PRODUCCION:
            raise TransicionIlegalError(
                f"El lote '{self._id}' ya está decidido "
                f"({self._estado.value})."
            )

        if not self._muestras:
            raise TransicionIlegalError(
                f"El lote '{self._id}' no tiene muestras."
            )

        if not self.todas_cerradas():
            raise TransicionIlegalError(
                f"El lote '{self._id}': no todas las muestras están cerradas."
            )

        if self.porcentaje_no_conforme() > 5:
            self._estado = EstadoLote.RECHAZADO
        else:
            self._estado = EstadoLote.APROBADO

        return self._estado

    # --- Consultas (sin efectos secundarios) ---

    def _muestras_cerradas(self):
        """Filtra las muestras que se encuentran en un estado final."""
        return filter(
            lambda m: m.estado in Lote.ESTADOS_FINALES,
            self._muestras.values()
        )

    def porcentaje_no_conforme(self):
        """Calcula el porcentaje de muestras no conformes sin redondear."""
        total_muestras = len(self._muestras)

        if total_muestras == 0:
            return 0

        # Seleccionamos únicamente las muestras no conformes.
        no_conformes = filter(
            lambda m: m.estado == EstadoMuestra.NO_CONFORME,
            self._muestras.values()
        )

        # Contamos las muestras filtradas.
        cantidad_no_conformes = len(list(no_conformes))

        return cantidad_no_conformes / total_muestras * 100

    def todas_cerradas(self):
        """Verifica si todas las muestras están en un estado final."""
        return all(
            map(
                lambda m: m.estado in Lote.ESTADOS_FINALES,
                self._muestras.values()
            )
        )

    def total_defectos_criticos(self):
        """Cuenta el total de defectos críticos de las muestras cerradas."""

        # Primero se filtran las muestras cerradas.
        # Luego cada muestra se transforma en su cantidad de defectos críticos
        # (filtrando sus defectos con gravedad 5).
        # Finalmente se suman esas cantidades.
        return sum(
            map(
                lambda m: len(list(filter(lambda d: d.es_critico(), m.defectos))),
                self._muestras_cerradas()
            )
        )

    def conteo_por_tipo(self):
        """Retorna un dict {tipo: cantidad} con los defectos
        encontrados en muestras cerradas."""
        conteo = {}

        # Se recorren únicamente las muestras cerradas.
        for muestra in self._muestras_cerradas():
            for defecto in muestra.defectos:
                conteo[defecto.tipo] = conteo.get(defecto.tipo, 0) + 1

        return conteo

    # --- Conjuntos: tipos de defecto ---

    def tipos_de_defecto(self):
        """Conjunto (set) con los tipos de defecto de las muestras cerradas, sin repetir.
        update() agrega al conjunto todos los elementos de un iterable."""
        tipos = set()
        for muestra in self._muestras_cerradas():
            tipos.update(map(lambda d: d.tipo, muestra.defectos))
        return tipos

    def tipos_en_comun(self, otro):
        """Tipos de defecto que aparecen en los DOS lotes (intersección, &)."""
        return self.tipos_de_defecto() & self._validar_lote(otro).tipos_de_defecto()

    def tipos_exclusivos(self, otro):
        """Tipos de defecto que aparecen en UNO SOLO de los dos lotes
        (diferencia simétrica, ^)."""
        return self.tipos_de_defecto() ^ self._validar_lote(otro).tipos_de_defecto()

    @staticmethod
    def _validar_lote(otro):
        if not isinstance(otro, Lote):
            raise DatosInvalidosError(f"Se esperaba un Lote, recibido: {type(otro).__name__}")
        return otro

    # --- Índices con árbol AVL (árboles: Unidad 7; recursión: Unidad 8) ---

    def arbol_muestras_por_cantidad(self):
        """Retorna un ArbolAVL con las muestras del lote, indexadas por cantidad
        de unidades. Las muestras con la misma cantidad comparten nodo."""
        arbol = ArbolAVL()
        for muestra in self._muestras.values():
            arbol.insertar(muestra.cantidad, muestra)
        return arbol

    def arbol_defectos_por_gravedad(self):
        """Retorna un ArbolAVL con los defectos de las muestras cerradas, indexados
        por gravedad (1 a 5). Como hay a lo sumo 5 claves, el árbol tiene a lo sumo
        5 nodos. Los críticos se obtienen con arbol.buscar(5)."""
        arbol = ArbolAVL()
        for muestra in self._muestras_cerradas():
            for defecto in muestra.defectos:
                arbol.insertar(defecto.gravedad, defecto)
        return arbol

    def __repr__(self):
        return (
            f"Lote(id={self._id}, nombre_componentes='{self._nombre_componentes}', "
            f"cantidad_fabricada={self._cantidad_fabricada}, "
            f"estado={self._estado.value}, muestras={len(self._muestras)})"
        )