from classes.procedimiento import Procedimiento
from classes.defecto import DefectoDimensional


class ProcedimientoDimensional(Procedimiento):
    """Compara mediciones contra tolerancias (mín/máx) y genera defectos DIMENSIONAL."""

    CLASE_DEFECTO = DefectoDimensional

    def __init__(self, unidad_medida="mm", **kwargs):
        kwargs.setdefault("categoria_equipo_requerida", "Dimensional")
        super().__init__(**kwargs)
        self._unidad_medida = unidad_medida

    @property
    def unidad_medida(self):
        return self._unidad_medida

    def evaluar(self, observaciones):
        """Evalúa cada observación dimensional. Si el valor medido queda fuera
        del rango [tolerancia_min, tolerancia_max], genera un defecto con
        gravedad calculada."""
        # Primero se filtran las observaciones fuera de tolerancia (desviación > 0).
        # Luego cada observación filtrada se transforma en un DefectoDimensional,
        # que guarda la medición que lo originó.
        return list(
            map(
                lambda obs: DefectoDimensional(
                    descripcion=obs.descripcion,
                    gravedad=self._calcular_gravedad(obs),
                    valor_medido=obs.valor_medido,
                    tolerancia_min=obs.tolerancia_min,
                    tolerancia_max=obs.tolerancia_max,
                    unidad=self._unidad_medida
                ),
                filter(lambda obs: obs.desviacion > 0, observaciones)
            )
        )

    def _calcular_gravedad(self, obs):
        """Calcula la gravedad basada en el exceso de desviación sobre la tolerancia."""
        if obs.tolerancia == 0:
            return 5
        exceso = obs.desviacion / obs.tolerancia
        if exceso <= 0.25:
            return 1
        if exceso <= 0.5:
            return 2
        if exceso <= 1.0:
            return 3
        if exceso <= 2.0:
            return 4
        return 5
