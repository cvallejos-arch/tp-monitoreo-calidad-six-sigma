import uuid
from abc import ABC, abstractmethod

from classes.entidad import Entidad
from classes.validacion import validar_entero, validar_nombre_tecnico
from classes.excepciones import DatosInvalidosError
from classes.defecto import Defecto


class Procedimiento(Entidad, ABC):
    """Clase abstracta: define el contrato de toda inspección (límite de gravedad,
    requisitos de equipo y certificación) y exige implementar evaluar().
    No se puede instanciar directamente: solo sus subclases concretas."""

    # Clase de defecto que produce cada procedimiento. Cada subclase la redefine
    # para que la inspección pueda verificar la coherencia de los defectos.
    CLASE_DEFECTO = Defecto

    def __init__(self, limite_gravedad_acumulada, categoria_equipo_requerida,
                 certificacion_requerida=None, **kwargs):
        self._id = uuid.uuid4()
        self._limite_gravedad_acumulada = validar_entero(
            limite_gravedad_acumulada, "limite_gravedad_acumulada"
        )
        if self._limite_gravedad_acumulada <= 0:
            raise DatosInvalidosError(
                f"El límite de gravedad acumulada debe ser positivo, "
                f"recibido: {limite_gravedad_acumulada}"
            )
        self._categoria_equipo_requerida = validar_nombre_tecnico(
            categoria_equipo_requerida, "categoria_equipo_requerida"
        )
        if certificacion_requerida is not None:
            validar_nombre_tecnico(certificacion_requerida, "certificacion_requerida")
        self._certificacion_requerida = certificacion_requerida

    @property
    def id(self):
        return self._id

    @property
    def limite_gravedad_acumulada(self):
        return self._limite_gravedad_acumulada

    @property
    def categoria_equipo_requerida(self):
        return self._categoria_equipo_requerida

    @property
    def certificacion_requerida(self):
        return self._certificacion_requerida

    @abstractmethod
    def evaluar(self, observaciones):
        """Evalúa observaciones y retorna una lista de defectos de CLASE_DEFECTO.
        Cada subclase la implementa con su propio criterio (polimorfismo)."""

    def __repr__(self):
        return (
            f"{type(self).__name__}(id={self._id}, "
            f"limite_gravedad_acumulada={self._limite_gravedad_acumulada}, "
            f"categoria_equipo_requerida='{self._categoria_equipo_requerida}', "
            f"certificacion_requerida={self._certificacion_requerida})"
        )