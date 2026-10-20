"""Generador de casos aleatorios para probar el sistema (no es parte del dominio).

Las clases del dominio no usan azar: con los mismos datos dan siempre el mismo
resultado. El azar se usa SOLO para inventar observaciones y simular inspecciones.

Se usa un generador propio, random.Random(semilla), en lugar del random global:
- con la misma semilla se repite exactamente el mismo caso (sirve para la defensa);
- no altera el azar de ningún otro código.
"""
import random

from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.validacion import validar_cantidad
from classes.excepciones import DatosInvalidosError


def _validar_probabilidad(valor, nombre_campo):
    """Valida que el valor sea un número entre 0 y 1 (ambos incluidos)."""
    if not isinstance(valor, (int, float)) or isinstance(valor, bool) or not 0 <= valor <= 1:
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe ser un número entre 0 y 1, recibido: {valor}"
        )
    return valor


class Simulador:
    """Inventa observaciones visuales y dimensionales, y simula inspecciones completas."""

    # Descripciones posibles de un defecto visual (se elige una al azar)
    DEFECTOS_VISUALES = ("Rayadura", "Mancha", "Abolladura", "Fisura", "Decoloración", "Rebaba")

    def __init__(self, semilla=None):
        """semilla=None: un caso distinto cada vez. Un número: siempre el mismo caso."""
        self._semilla = semilla
        self._rng = random.Random(semilla)

    @property
    def semilla(self):
        return self._semilla

    # --- Observaciones ---

    def observaciones_visuales(self, cantidad, prob_defecto=0.2):
        """Genera `cantidad` observaciones visuales. Cada una tiene probabilidad
        `prob_defecto` de tener un defecto, con gravedad al azar entre 1 y 5."""
        validar_cantidad(cantidad)
        _validar_probabilidad(prob_defecto, "prob_defecto")
        return list(map(lambda _: self._observacion_visual(prob_defecto), range(cantidad)))

    def _observacion_visual(self, prob_defecto):
        if self._rng.random() < prob_defecto:           # random(): número entre 0 y 1
            descripcion = self._rng.choice(Simulador.DEFECTOS_VISUALES)
            gravedad = self._rng.randint(1, 5)             # randint incluye 1 y 5
            return ObservacionVisual(descripcion, True, gravedad)
        return ObservacionVisual("Sin defectos observados", False)

    def observaciones_dimensionales(self, cantidad, tolerancia_min, tolerancia_max,
                                    dispersion=0.2):
        """Genera `cantidad` mediciones alrededor del rango [tolerancia_min, tolerancia_max].
        `dispersion` indica cuánto pueden salirse, como fracción del ancho del rango
        (0 = siempre dentro; 0.2 = hasta un 20 % del rango por arriba o por abajo)."""
        validar_cantidad(cantidad)
        _validar_probabilidad(dispersion, "dispersion")
        if tolerancia_min > tolerancia_max:
            raise DatosInvalidosError("La tolerancia mínima no puede ser mayor que la máxima")

        margen = (tolerancia_max - tolerancia_min) * dispersion
        return list(map(
            lambda i: ObservacionDimensional(
                round(self._rng.uniform(tolerancia_min - margen, tolerancia_max + margen), 3),
                tolerancia_min,
                tolerancia_max,
                f"Medición {i + 1}"
            ),
            range(cantidad)
        ))

    def observaciones_para(self, procedimiento, cantidad, prob_defecto=0.2,
                           tolerancia_min=9.0, tolerancia_max=10.0, dispersion=0.2):
        """Genera las observaciones que corresponden al tipo de procedimiento:
        visuales para un ProcedimientoVisual y dimensionales para uno dimensional."""
        if isinstance(procedimiento, ProcedimientoVisual):
            return self.observaciones_visuales(cantidad, prob_defecto)
        return self.observaciones_dimensionales(cantidad, tolerancia_min, tolerancia_max,
                                                dispersion)

    # --- Simulación de un lote completo ---

    def simular_lote(self, empresa, lote, profesional, equipo, procedimiento, fecha,
                     max_observaciones=3, **opciones):
        """Inspecciona todas las muestras pendientes del lote en el orden de la cola.
        Cada muestra recibe entre 1 y `max_observaciones` observaciones al azar
        (`**opciones` se pasa a observaciones_para: prob_defecto, tolerancias, dispersion).
        Las validaciones del dominio se aplican igual que en una inspección manual.
        Retorna la lista de inspecciones realizadas."""
        validar_cantidad(max_observaciones)
        inspecciones = []
        while lote.siguiente_muestra_pendiente() is not None:
            cantidad = self._rng.randint(1, max_observaciones)
            observaciones = self.observaciones_para(procedimiento, cantidad, **opciones)
            insp = empresa.lanzar_siguiente_inspeccion(
                lote, profesional, equipo, procedimiento, fecha
            )
            insp.ejecutar(observaciones)
            insp.cerrar()
            inspecciones.append(insp)
        return inspecciones
