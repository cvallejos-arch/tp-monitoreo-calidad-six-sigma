<<<<<<< HEAD
from validacion import validar_id, validar_texto
import uuid

class Equipo:
    def __init__(self, categoria, fecha_calibracion):
        validar_texto(categoria, "La categoría")
=======
from validacion import validar_texto

class Equipo:
    def __init__(self, id, categoria, fecha_calibracion):
        validar_texto(categoria)
>>>>>>> d6b8e214f84af8386ad26841bbccc3f7bec4924b

        self._id = uuid.uuid4()
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    def get_id(self):
        return self._id

    def get_categoria(self):
        return self._categoria

    def get_fecha_calibracion(self):
        return self._fecha_calibracion

    def esta_calibrado(self, fecha):
        return 0 <= (fecha - self._fecha_calibracion).days <= 182

    def es_compatible(self, categoria_requerida):
        return self._categoria == categoria_requerida