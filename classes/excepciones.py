class CalidadError(Exception):
    """Excepción base del sistema de monitoreo de calidad.
    Soporta **detalles para adjuntar contexto estructurado de diagnóstico."""
    def __init__(self, mensaje="Ocurrió un error en el sistema de calidad", **detalles):
        super().__init__(mensaje)
        self._detalles = detalles

    @property
    def detalles(self):
        """Retorna el diccionario de metadatos contextuales del error."""
        return dict(self._detalles)


class DatosInvalidosError(CalidadError):
    """Para datos inválidos: números <= 0, gravedades fuera de rango [1, 5],
    textos vacíos, fechas inválidas."""
    def __init__(self, mensaje="El dato ingresado es inválido", **detalles):
        super().__init__(mensaje, **detalles)


class EquipoNoAptoError(CalidadError):
    """Para discrepancia de categoría o calibración vencida (>182 días)."""
    def __init__(self, mensaje="El equipo no es apto para la inspección solicitada", **detalles):
        super().__init__(mensaje, **detalles)


class CertificacionNoVigenteError(CalidadError):
    """Para profesional no certificado o certificación vencida."""
    def __init__(self, mensaje="El profesional no cuenta con la certificación requerida o vigente", **detalles):
        super().__init__(mensaje, **detalles)


class TransicionIlegalError(CalidadError):
    """Para modificaciones a muestras o lotes cerrados, o transiciones de estado ilegales."""
    def __init__(self, mensaje="No se puede realizar la transición de estado solicitada", **detalles):
        super().__init__(mensaje, **detalles)


class InspeccionInvalidaError(CalidadError):
    """Para operaciones inválidas sobre una inspección cerrada."""
    def __init__(self, mensaje="La inspección no puede ser ejecutada o cerrada", **detalles):
        super().__init__(mensaje, **detalles)

class EstructuraVaciaError(CalidadError):
    """Para desapilar/desencolar/consultar una estructura vacía."""
    def __init__(self, mensaje="La estructura está vacía", **detalles):
        super().__init__(mensaje, **detalles)