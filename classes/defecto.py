from classes.validacion import validar_texto, validar_descripcion, validar_gravedad

class Defecto:
    def __init__(self, tipo, descripcion, gravedad):
        validar_texto(tipo)
        validar_descripcion(descripcion)
        validar_gravedad(gravedad)

        self._tipo = tipo
        self._descripcion = descripcion
        self._gravedad = gravedad

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
        return Defecto(
            self._tipo,
            self._descripcion,
            self._gravedad
        )