from classes.excepciones import DatosInvalidosError
from classes.validacion import validar_descripcion


class ObservacionDimensional:
    """Observación de una medición dimensional con valor medido y tolerancias."""

    def __init__(self, valor_medido, tolerancia_min, tolerancia_max, descripcion):
        self._descripcion = validar_descripcion(descripcion)

        if not isinstance(valor_medido, (int, float)) or isinstance(valor_medido, bool):
            raise DatosInvalidosError("El valor medido debe ser un número")

        if not isinstance(tolerancia_min, (int, float)) or isinstance(tolerancia_min, bool):
            raise DatosInvalidosError("La tolerancia mínima debe ser un número")

        if not isinstance(tolerancia_max, (int, float)) or isinstance(tolerancia_max, bool):
            raise DatosInvalidosError("La tolerancia máxima debe ser un número")

        if tolerancia_min > tolerancia_max:
            raise DatosInvalidosError(
                "La tolerancia mínima no puede ser mayor que la máxima"
            )

        self._valor_medido = valor_medido
        self._tolerancia_min = tolerancia_min
        self._tolerancia_max = tolerancia_max

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

    @property
    def desviacion(self):
        """Calcula la desviación del valor medido respecto a las tolerancias.
        Positiva si fuera de rango, 0 si dentro."""
        if self._valor_medido > self._tolerancia_max:
            return self._valor_medido - self._tolerancia_max
        elif self._valor_medido < self._tolerancia_min:
            return self._tolerancia_min - self._valor_medido
        return 0.0

    @property
    def tolerancia(self):
        """Retorna el rango de tolerancia (max - min) como referencia para el cálculo
        de gravedad en el procedimiento dimensional."""
        rango = self._tolerancia_max - self._tolerancia_min
        return rango if rango > 0 else 1.0  # Evitar división por cero

    def __repr__(self):
        return (
            f"ObservacionDimensional(valor_medido={self._valor_medido}, "
            f"tolerancia_min={self._tolerancia_min}, "
            f"tolerancia_max={self._tolerancia_max}, "
            f"descripcion='{self._descripcion}')"
        )