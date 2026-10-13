from classes.validacion import validar_texto, validar_descripcion, validar_gravedad
from classes.excepciones import DatosInvalidosError


class Defecto:
    """Desviación observada. Inmutable: solo tiene getters (sin setters)."""

    def __init__(self, tipo, descripcion, gravedad):
        self._tipo = validar_texto(tipo, "tipo")
        self._descripcion = validar_descripcion(descripcion)
        self._gravedad = validar_gravedad(gravedad)

    @property
    def tipo(self):
        return self._tipo

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def gravedad(self):
        return self._gravedad

    def es_critico(self):
        return self._gravedad == 5

    def copia(self):
        """Crea una copia inmutable del defecto."""
        return Defecto(
            self._tipo,
            self._descripcion,
            self._gravedad
        )

    def __repr__(self):
        return (
            f"Defecto(tipo='{self._tipo}', descripcion='{self._descripcion}', "
            f"gravedad={self._gravedad})"
        )


class DefectoVisual(Defecto):
    """Defecto producido por un ProcedimientoVisual (anomalía estética o funcional)."""

    TIPO = "VISUAL"

    def __init__(self, descripcion, gravedad):
        super().__init__(DefectoVisual.TIPO, descripcion, gravedad)

    def copia(self):
        return DefectoVisual(self._descripcion, self._gravedad)


class DefectoDimensional(Defecto):
    """Defecto producido por un ProcedimientoDimensional. Además de los datos
    comunes, guarda la medición que lo originó. Es coherente con su procedimiento:
    el valor medido tiene que estar fuera del rango [tolerancia_min, tolerancia_max]."""

    TIPO = "DIMENSIONAL"

    def __init__(self, descripcion, gravedad, valor_medido, tolerancia_min,
                 tolerancia_max, unidad="mm"):
        super().__init__(DefectoDimensional.TIPO, descripcion, gravedad)

        for nombre, valor in (("valor_medido", valor_medido),
                              ("tolerancia_min", tolerancia_min),
                              ("tolerancia_max", tolerancia_max)):
            if not isinstance(valor, (int, float)) or isinstance(valor, bool):
                raise DatosInvalidosError(f"El campo '{nombre}' debe ser un número")

        if tolerancia_min > tolerancia_max:
            raise DatosInvalidosError("La tolerancia mínima no puede ser mayor que la máxima")

        if tolerancia_min <= valor_medido <= tolerancia_max:
            raise DatosInvalidosError(
                f"Un defecto dimensional requiere un valor fuera de tolerancia: "
                f"{valor_medido} está dentro de [{tolerancia_min}, {tolerancia_max}]"
            )

        self._valor_medido = valor_medido
        self._tolerancia_min = tolerancia_min
        self._tolerancia_max = tolerancia_max
        self._unidad = validar_texto(unidad, "unidad")

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
    def unidad(self):
        return self._unidad

    def copia(self):
        return DefectoDimensional(
            self._descripcion, self._gravedad, self._valor_medido,
            self._tolerancia_min, self._tolerancia_max, self._unidad
        )

    def __repr__(self):
        return (
            f"DefectoDimensional(descripcion='{self._descripcion}', "
            f"gravedad={self._gravedad}, valor_medido={self._valor_medido}, "
            f"rango=[{self._tolerancia_min}, {self._tolerancia_max}] {self._unidad})"
        )
