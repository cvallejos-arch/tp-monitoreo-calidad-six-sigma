import uuid
from datetime import timedelta

from classes.entidad import Entidad
from classes.validacion import validar_fecha_tipo, validar_nombre_tecnico


class Equipo(Entidad):
    # Una calibración vale 182 días (regla 4 de la consigna: "6 meses")
    DIAS_VALIDEZ_CALIBRACION = 182

    def __init__(self, categoria, fecha_calibracion):
        self._id = uuid.uuid4()
        self._categoria = validar_nombre_tecnico(categoria, "categoria")
        self._fecha_calibracion = validar_fecha_tipo(fecha_calibracion, "fecha_calibracion")

    @property
    def id(self):
        return self._id

    @property
    def categoria(self):
        return self._categoria

    @property
    def fecha_calibracion(self):
        return self._fecha_calibracion

    @property
    def fecha_vencimiento(self):
        """Último día en que el equipo sigue calibrado (calibración + 182 días)."""
        return self._fecha_calibracion + timedelta(days=Equipo.DIAS_VALIDEZ_CALIBRACION)

    def esta_calibrado(self, fecha):
        """Un equipo está calibrado si la fecha de calibración está dentro de
        los 182 días anteriores a la fecha de inspección (los extremos se incluyen).
        fecha_calibracion <= fecha_inspeccion y
        fecha_inspeccion - fecha_calibracion <= 182 días."""
        dias = (fecha - self._fecha_calibracion).days
        return 0 <= dias <= Equipo.DIAS_VALIDEZ_CALIBRACION

    def es_compatible(self, categoria_requerida):
        """Verifica si la categoría del equipo coincide con la requerida."""
        return self._categoria == categoria_requerida

    def __repr__(self):
        return (
            f"Equipo(id={self._id}, categoria='{self._categoria}', "
            f"fecha_calibracion={self._fecha_calibracion})"
        )