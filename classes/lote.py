from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad, validar_texto
from classes.excepciones import TransicionIlegalError, DatosInvalidosError
from classes.cola import Cola
import uuid


class Lote:
    # Estados en los que una muestra se considera cerrada (inspección finalizada).
    ESTADOS_FINALES = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)

    def __init__(self, nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = validar_texto(
            nombre_componentes,
            "nombre_componentes"
        )
        self._cantidad_fabricada = validar_cantidad(cantidad_fabricada)
        self._estado = EstadoLote.EN_PRODUCCION
        self._muestras = {}  # dict {muestra.id: muestra}
        self._pendientes = Cola(Muestra)

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
        self._pendientes.encolar(muestra)
        return muestra

 # --- Cola de pendientes ---

    def siguiente_muestra_pendiente(self):
        """Retorna la próxima muestra PENDIENTE en orden de creación, o None.
        NO la desencola: sigue al frente hasta que deje de estar PENDIENTE.
        Descarta del frente las muestras que ya no están pendientes (p. ej.
        inspeccionadas fuera de orden). No modifica muestras, reportes ni
        el estado del lote."""
        while not self._pendientes.esta_vacia():
            frente = self._pendientes.frente()
            if frente.estado == EstadoMuestra.PENDIENTE:
                return frente
            self._pendientes.desencolar()
        return None

    def pendientes_en_orden(self):
        """Genera las muestras PENDIENTE en orden de creación, sin tocar la cola."""
        for m in self._pendientes:      
            if m.estado == EstadoMuestra.PENDIENTE:
                yield m

  # --- Decisión del lote ---

    def decidir(self):
        """Decide el estado del lote basado en el porcentaje de muestras no conformes.
        RECHAZADO si > 5%, APROBADO si <= 5%. La decisión es final."""
        if self._estado != EstadoLote.EN_PRODUCCION:
            raise TransicionIlegalError(
                f"El lote '{self._id}' ya está decidido ({self._estado.value})."
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

    def porcentaje_no_conforme(self):
        """Calcula el porcentaje de muestras no conformes sin redondear."""
        total_muestras = len(self._muestras)
        if total_muestras == 0:
            return 0
        no_conforme_count = sum(
            map(lambda m: 1 if m.estado == EstadoMuestra.NO_CONFORME else 0,
                self._muestras.values())
        )
        return no_conforme_count / total_muestras * 100

    def todas_cerradas(self):
        """Verifica si todas las muestras están en un estado final."""
        estados_finales = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)
        return all(map(lambda m: m.estado in estados_finales, self._muestras.values()))

    def _muestras_cerradas(self):
        """Genera las muestras en estado final, de a una."""
        for m in self._muestras.values():
            if m.estado in (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME):
                yield m

    def _defectos_cerrados(self):
        """Genera los defectos de todas las muestras cerradas."""
        for m in self._muestras_cerradas():
            yield from m.defectos

    def total_defectos_criticos(self):
        """Cuenta el total de defectos críticos en muestras cerradas."""
        return sum(1 for d in self._defectos_cerrados() if d.es_critico())

    def conteo_por_tipo(self):
        """Retorna un dict {tipo: cantidad} de defectos en muestras cerradas."""
        conteo = {}
        for d in self._defectos_cerrados():
            conteo[d.tipo] = conteo.get(d.tipo, 0) + 1
        return conteo

    def __repr__(self):
        return (
            f"Lote(id={self._id}, nombre_componentes='{self._nombre_componentes}', "
            f"cantidad_fabricada={self._cantidad_fabricada}, "
            f"estado={self._estado.value}, muestras={len(self._muestras)})"
        )