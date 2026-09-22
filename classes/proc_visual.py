from classes.procedimiento import Procedimiento
from classes.defecto import Defecto


class ProcedimientoVisual(Procedimiento):

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
