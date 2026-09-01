#para importar en las clases se usa:
"""
from dominio.excepciones import (
    EquipoNoAptoException,
    CertificacionFaltanteException,
    TransicionIlegalException
)
"""


class CalidadException(Exception):
    """Excepción base del sistema de monitoreo de calidad."""
    def __init__(self, mensaje: str = "Ocurrió un error en el sistema de calidad"):
        super().__init__(mensaje)


class DatoInvalidoException(CalidadException):
    """Para errores en IDs vacíos, números <= 0 o gravedades fuera de rango [1, 5]."""
    pass


class EquipoNoAptoException(CalidadException):
    """Para discrepancia de categoría o calibración vencida (>182 días)."""
    pass


class CertificacionFaltanteException(CalidadException):
    """Para profesional no certificado o certificación vencida."""
    pass


class TransicionIlegalException(CalidadException):
    """Para modificaciones a muestras o lotes cerrados."""
    pass
