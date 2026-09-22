from classes.validacion import validar_texto, validar_rango_fechas


class Certificacion:
    def __init__(self, nombre, fecha_inicio, fecha_fin):
        self._nombre = validar_texto(nombre, "nombre_certificacion")
        validar_rango_fechas(fecha_inicio, fecha_fin)
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
        """Verifica si la certificación es vigente en la fecha dada (bornes inclusivos)."""
        return self._fecha_inicio <= fecha <= self._fecha_fin

    def __repr__(self):
        return (
            f"Certificacion(nombre='{self._nombre}', "
            f"fecha_inicio={self._fecha_inicio}, fecha_fin={self._fecha_fin})"
        )