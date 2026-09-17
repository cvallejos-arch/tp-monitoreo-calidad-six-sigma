from validacion import validar_texto, validar_rango_fechas

class Certificacion:
    def __init__(self, nombre, fecha_inicio, fecha_fin):
        validar_texto(nombre)
        validar_rango_fechas(fecha_inicio, fecha_fin)

        self._nombre = nombre
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin

    @property
    def nombre(self):
        return self._nombre

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def fecha_fin(self):
        return self._fecha_fin

    def es_vigente(self, fecha):
        return self._fecha_inicio <= fecha <= self._fecha_fin