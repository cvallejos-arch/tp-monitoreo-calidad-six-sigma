import uuid

class Profesional:
    def __init__(self, nombre):
        self._id = uuid.uuid4()
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
    
    def __str__(self):
        return f'ID: {self._id}; Nombre: {self._nombre}'

P = Profesional('Martin P')
print(P)