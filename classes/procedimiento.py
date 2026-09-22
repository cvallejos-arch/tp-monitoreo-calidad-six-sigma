import uuid
from classes.validacion import validar_texto, validar_entero


class Procedimiento:

    def __init__(self, limite_gravedad_acumulada, categoria_equipo_requerida,
                 certificacion_requerida=None):
        self._id = uuid.uuid4()
        self._limite_gravedad_acumulada = validar_entero(
            limite_gravedad_acumulada, "limite_gravedad_acumulada"
        )
        if self._limite_gravedad_acumulada <= 0:
            from classes.excepciones import DatosInvalidosError
            raise DatosInvalidosError(
                f"El límite de gravedad acumulada debe ser positivo, "
                f"recibido: {limite_gravedad_acumulada}"
            )
        self._categoria_equipo_requerida = validar_texto(
            categoria_equipo_requerida, "categoria_equipo_requerida"
        )
        if certificacion_requerida is not None:
            validar_texto(certificacion_requerida, "certificacion_requerida")
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

    def evaluar(self, observaciones):
        """Evalúa observaciones y retorna una lista de defectos.
        Debe ser implementado por las subclases (polimorfismo)."""
        raise NotImplementedError("Se implementa en las subclases")

    def __repr__(self):
        return (
            f"Procedimiento(id={self._id}, "
            f"limite_gravedad_acumulada={self._limite_gravedad_acumulada}, "
            f"categoria_equipo_requerida='{self._categoria_equipo_requerida}', "
            f"certificacion_requerida={self._certificacion_requerida})"
        )