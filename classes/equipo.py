from validacion import validar_texto
import uuid

class Equipo:
    def __init__(self, categoria, fecha_calibracion):
        validar_texto(categoria)

        self._id = uuid.uuid4()
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    @property
    def id(self):
        return self._id

    @property
    def categoria(self):
        return self._categoria

    @property
    def fecha_calibracion(self):
        return self._fecha_calibracion

    def esta_calibrado(self, fecha):
        return 0 <= (fecha - self._fecha_calibracion).days <= 182

    def es_compatible(self, categoria_requerida):
        return self._categoria == categoria_requerida