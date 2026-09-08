#para importar en las clases se usa:

from excepciones import (
    EquipoNoAptoException,
    CertificacionFaltanteException,
    TransicionIlegalException,
    DatoInvalidoException
)



class CalidadException(Exception):
    """Excepción base del sistema de monitoreo de calidad."""
    def __init__(self, mensaje: str = "Ocurrió un error en el sistema de calidad"):
        super().__init__(mensaje)


class DatoInvalidoException(CalidadException):
    """Para errores números <= 0 o gravedades fuera de rango [1, 5]."""
    def __init__(self, mensaje: str = "El dato ingresado es invalido" ):
        super().__init__(mensaje)


class EquipoNoAptoException(CalidadException):
    """Para discrepancia de categoría o calibración vencida (>182 días)."""
    def __init__(self, mensaje:str = "El equipo no es apto para la insepeccion solicitada"):
        super().__init__(mensaje)



class CertificacionFaltanteException(CalidadException):
    """Para profesional no certificado o certificación vencida."""
    def __init__(self, mensaje: str = "El profesional no cuenta con la certificacion requerida o vigente"):
        super().__init__(mensaje)


class TransicionIlegalException(CalidadException):
    """Para modificaciones a muestras o lotes cerrados."""
    def __init__(self, mensaje: str = "No se puede realizar otra transicion de estado"):
        super().__init__(mensaje)
