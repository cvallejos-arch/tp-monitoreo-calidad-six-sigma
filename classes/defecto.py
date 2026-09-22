from classes.validacion import validar_texto, validar_descripcion, validar_gravedad


class Defecto:
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