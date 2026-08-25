from enum import Enum

class EstadoLote(Enum):
    EN_PRODUCCION = "EN_PRODUCCION"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"