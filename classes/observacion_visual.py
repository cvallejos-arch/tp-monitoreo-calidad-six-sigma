from classes.validacion import validar_descripcion, validar_rango_entero
from classes.excepciones import DatosInvalidosError


class ObservacionVisual:
    """Observación de una inspección visual con detección de defecto y gravedad."""

    def __init__(self, descripcion, defecto_detectado, gravedad=None):
        self._descripcion = validar_descripcion(descripcion)

        if not isinstance(defecto_detectado, bool):
            raise DatosInvalidosError(
                "El valor de defecto_detectado debe ser un booleano"
            )

        self._defecto_detectado = defecto_detectado

        if defecto_detectado:
            if gravedad is None:
                raise DatosInvalidosError(
                    "Debe especificarse la gravedad cuando hay un defecto detectado"
                )
            self._gravedad = validar_rango_entero(gravedad, 1, 5, "gravedad")
        else:
            self._gravedad = None

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def defecto_detectado(self):
        return self._defecto_detectado

    @property
    def gravedad(self):
        return self._gravedad

    def __repr__(self):
        return (
            f"ObservacionVisual(descripcion='{self._descripcion}', "
            f"defecto_detectado={self._defecto_detectado}, "
            f"gravedad={self._gravedad})"
        )