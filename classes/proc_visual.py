from classes.procedimiento import Procedimiento
from classes.defecto import Defecto


class ProcedimientoVisual(Procedimiento):

    def __init__(self, nivel_iluminacion_minimo=None, **kwargs):
        kwargs.setdefault("categoria_equipo_requerida", "Visual")
        super().__init__(**kwargs)
        self._nivel_iluminacion_minimo = nivel_iluminacion_minimo

    @property
    def nivel_iluminacion_minimo(self):
        return self._nivel_iluminacion_minimo

    def evaluar(self, observaciones):
        """Evalúa cada observación visual. Si defecto_detectado es True,
        genera un defecto con la gravedad indicada."""
        defectos = []
        for obs in observaciones:
            if obs.defecto_detectado:
                defectos.append(
                    Defecto(
                        tipo="VISUAL",
                        descripcion=obs.descripcion,
                        gravedad=obs.gravedad
                    )
                )
        return defectos
