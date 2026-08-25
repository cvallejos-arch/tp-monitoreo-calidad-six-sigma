class Equipo:
    def __init__(self, id, categoria, fecha_calibracion):
        self._id = id
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    def get_id(self):
        return self._id

    def get_categoria(self):
        return self._categoria

    def get_fecha_calibracion(self):
        return self._fecha_calibracion

    def esta_calibrado(self, fecha):
        pass

    def es_compatible(self, categoria_requerida):
        pass