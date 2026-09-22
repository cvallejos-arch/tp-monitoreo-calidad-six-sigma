class CalidadError(Exception):
    """Excepción base del sistema de monitoreo de calidad."""
    def __init__(self, mensaje="Ocurrió un error en el sistema de calidad"):
        super().__init__(mensaje)


class DatosInvalidosError(CalidadError):
    """Para datos inválidos: números <= 0, gravedades fuera de rango [1, 5],
    textos vacíos, fechas inválidas."""
    def __init__(self, mensaje="El dato ingresado es inválido"):
        super().__init__(mensaje)


class EquipoNoAptoError(CalidadError):
    """Para discrepancia de categoría o calibración vencida (>182 días)."""
    def __init__(self, mensaje="El equipo no es apto para la inspección solicitada"):
        super().__init__(mensaje)


class CertificacionNoVigenteError(CalidadError):
    """Para profesional no certificado o certificación vencida."""
    def __init__(self, mensaje="El profesional no cuenta con la certificación requerida o vigente"):
        super().__init__(mensaje)


class TransicionIlegalError(CalidadError):
    """Para modificaciones a muestras o lotes cerrados, o transiciones de estado ilegales."""
    def __init__(self, mensaje="No se puede realizar la transición de estado solicitada"):
        super().__init__(mensaje)


class InspeccionInvalidaError(CalidadError):
    """Para operaciones inválidas sobre una inspección cerrada."""
    def __init__(self, mensaje="La inspección no puede ser ejecutada o cerrada"):
        super().__init__(mensaje)
