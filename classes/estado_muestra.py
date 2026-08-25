from enum import Enum
class EstadoMuestra(Enum):
    PENDIENTE = "PENDIENTE"
    EN_INSPECCION = "EN_INSPECCION"
    CONFORME = "CONFORME"
    NO_CONFORME = "NO_CONFORME"
