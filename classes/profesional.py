class Profesional:
    def __init__(self, id, nombre):
        self._id = id
        self._nombre = nombre
        self._certificaciones = []

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def agregar_certificacion(self, cert):
        pass

    def tiene_certificacion_vigente(self, nombre, fecha):
        pass