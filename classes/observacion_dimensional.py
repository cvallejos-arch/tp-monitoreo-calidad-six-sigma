from classes.excepciones import DatosInvalidosError
from classes.validacion import validar_texto

class ObservacionDimensional:
    def __init__(self, valor_medido, tolerancia_min, tolerancia_max, descripcion):
        validar_texto(descripcion)

        if not isinstance(valor_medido, (int,float)) or isinstance(valor_medido, bool):
            raise DatosInvalidosError("El valor medido debe ser un número")

        if not isinstance(tolerancia_min, (int,float)) or isinstance(tolerancia_min, bool):
            raise DatosInvalidosError("La tolerancia mínima debe ser un número")

        if not isinstance(tolerancia_max, (int,float)) or isinstance(tolerancia_max, bool):
            raise DatosInvalidosError("La tolerancia máxima debe ser un número")

        if tolerancia_min > tolerancia_max:
            raise DatosInvalidosError("La tolerancia mínima no puede ser mayor que la máxima")

        self._valor_medido = valor_medido
        self._tolerancia_min = tolerancia_min
        self._tolerancia_max = tolerancia_max
        self._descripcion = descripcion

    @property
    def valor_medido(self):
        return self._valor_medido

    @property
    def tolerancia_min(self):
        return self._tolerancia_min

    @property
    def tolerancia_max(self):
        return self._tolerancia_max

    @property
    def descripcion(self):
        return self._descripcion

    def __repr__(self):
        return (
            "ObservacionDimensional(valor_medido=" + str(self._valor_medido) +
            ", tolerancia_min=" + str(self._tolerancia_min) +
            ", tolerancia_max=" + str(self._tolerancia_max) +
            ", descripcion=" + self._descripcion +
            ")"
        )