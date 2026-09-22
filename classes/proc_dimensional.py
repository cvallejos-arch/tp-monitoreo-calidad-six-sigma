from classes.procedimiento import Procedimiento
from classes.defecto import Defecto


class ProcedimientoDimensional(Procedimiento):


    def evaluar(self, observaciones):
        """Evalúa cada observación dimensional. Si la desviación es mayor
        que la tolerancia, genera un defecto con gravedad calculada."""
        defectos = []
        for obs in observaciones:
            if obs.desviacion > 0:
                gravedad = self._calcular_gravedad(obs)
                defectos.append(
                    Defecto(
                        tipo="DIMENSIONAL",
                        descripcion=f"Desviación dimensional: medido={obs.valor_medido}, "
                                    f"rango=[{obs.tolerancia_min}, {obs.tolerancia_max}]",
                        gravedad=gravedad
                    )
                )
        return defectos

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
