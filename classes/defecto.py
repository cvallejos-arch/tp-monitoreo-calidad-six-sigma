class Defecto:
    def __init__(self, tipo, descripcion, gravedad):
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
        pass

    def copia(self):
        pass