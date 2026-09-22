from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad
from classes.excepciones import TransicionIlegalError
from classes.reporte import Reporte
import uuid


class Muestra:
    def __init__(self, cantidad):
        self._id = uuid.uuid4()
        self._cantidad = validar_cantidad(cantidad)
        self._estado = EstadoMuestra.PENDIENTE
        self._defectos = []
        self._lote_id = None
        self._inspeccion = None
        self._reporte = None

    @property
    def id(self):
        return self._id

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def estado(self):
        return self._estado

    @property
    def defectos(self):
        """Retorna una tupla inmutable de los defectos registrados."""
        return tuple(self._defectos)

    @property
    def lote_id(self):
        return self._lote_id

    @property
    def inspeccion(self):
        return self._inspeccion

    @property
    def reporte(self):
        return self._reporte

    # --- Gestión de la pertenencia al lote ---

    def asignar_lote(self, lote_id):
        """Asigna la muestra a un lote. Una muestra no puede moverse a otro lote."""
        if self._lote_id is not None:
            raise TransicionIlegalError(
                f"La muestra '{self._id}' ya pertenece al lote "
                f"'{self._lote_id}' y no puede moverse a '{lote_id}'."
            )
        self._lote_id = lote_id

    def asignar_inspeccion(self, inspeccion):
        """Asigna la inspección a la muestra (encapsulación correcta)."""
        if self._inspeccion is not None:
            raise TransicionIlegalError(
                f"La muestra '{self._id}' ya tiene una inspección asignada."
            )
        self._inspeccion = inspeccion

    # --- Transiciones de estado ---

    def iniciar_inspeccion(self):
        """Transición PENDIENTE → EN_INSPECCION."""
        if self._estado != EstadoMuestra.PENDIENTE:
            raise TransicionIlegalError(
                f"No se pudo iniciar la inspección: la muestra '{self._id}' "
                f"está en estado {self._estado.value}, se espera PENDIENTE."
            )
        self._estado = EstadoMuestra.EN_INSPECCION

    def agregar_defecto(self, defecto):
        """Agrega un defecto a la muestra. Solo se puede en estado EN_INSPECCION."""
        if self._estado != EstadoMuestra.EN_INSPECCION:
            raise TransicionIlegalError(
                f"No se pudo agregar un defecto: la muestra '{self._id}' "
                f"está en estado {self._estado.value}, se espera EN_INSPECCION."
            )
        self._defectos.append(defecto)

    def cerrar(self, limite_gravedad):
        """Cierra la muestra determinando su conformidad.
        NO_CONFORME si tiene defecto crítico (gravedad 5) o suma > límite.
        CONFORME en caso contrario. Ambos estados son finales."""
        if self._estado != EstadoMuestra.EN_INSPECCION:
            raise TransicionIlegalError(
                f"No se pudo cerrar la muestra '{self._id}': "
                f"está en estado {self._estado.value}, se espera EN_INSPECCION."
            )

        if self.tiene_critico() or self.suma_gravedades() > limite_gravedad:
            self._estado = EstadoMuestra.NO_CONFORME
        else:
            self._estado = EstadoMuestra.CONFORME

        # Generar reporte si es no conforme
        if self._estado == EstadoMuestra.NO_CONFORME:
            self._reporte = Reporte(
                muestra_id=self._id,
                lote_id=self._lote_id,
                profesional_id=self._inspeccion.profesional_id,
                fecha=self._inspeccion.fecha,
                defectos=self._defectos
            )

    # --- Cálculos con sum(), any(), map() ---

    def suma_gravedades(self):
        """Suma de gravedades de todos los defectos, usando sum() + map()."""
        return sum(map(lambda d: d.gravedad, self._defectos))

    def tiene_critico(self):
        """Verifica si hay al menos un defecto crítico (gravedad 5), usando any() + map()."""
        return any(map(lambda d: d.es_critico(), self._defectos))

    def __repr__(self):
        return (
            f"Muestra(id={self._id}, cantidad={self._cantidad}, "
            f"estado={self._estado.value}, defectos={len(self._defectos)}, "
            f"lote_id={self._lote_id})"
        )
