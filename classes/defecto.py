from validacion import validar_texto, validar_gravedad

class Defecto:
    def __init__(self, tipo, descripcion, gravedad):
        validar_texto(tipo)
        validar_texto(descripcion)
        validar_gravedad(gravedad)

        self._tipo = tipo
        self._descripcion = descripcion
        self._gravedad = gravedad

    def get_tipo(self):
        return self._tipo

    def get_descripcion(self):
        return self._descripcion

    def get_gravedad(self):
        return self._gravedad

    def es_critico(self):
        return self._gravedad == 5

    def copia(self):
        return Defecto(
            self._tipo,
            self._descripcion,
            self._gravedad
        )     