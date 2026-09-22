from classes.validacion import validar_texto, validar_rango_entero
from classes.excepciones import DatosInvalidosError

class ObservacionVisual:
    def __init__(self, descipcion, defecto_detectado, gravedad= None):
        validar_texto(descipcion)

        if defecto_detectado is not None:
            if not isinstance(defecto_detectado, bool):
                raise DatosInvalidosError("El valor de defecto_detectado debe ser un booleano")

        self._defecto_detectado = defecto_detectado


        if defecto_detectado:
            if gravedad is None:
                raise DatosInvalidosError("Debe especificarse la gravedad cuando hay un defecto detectado") 
            self._gravedad = validar_rango_entero(gravedad, 1, 5, "gravedad")
        else:
            self._gravedad = None

        self._descripcion = descipcion

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
            "ObservacionVisual(descripcion=" + self._descripcion +
            ", defecto_detectado=" + str(self._defecto_detectado) +
            ", gravedad=" + str(self._gravedad) +
            ")"
        )