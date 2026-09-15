from classes.procedimiento import Procedimiento
from classes.defecto import Defecto


class ProcedimientoDimensional(Procedimiento):
    def evaluar(self, observaciones):
        defectos = []
        for obs in observaciones:
            if obs.desviacion > obs.tolerancia:
                gravedad = self._calcular_gravedad(obs)
                defectos.append(
                    Defecto(
                        tipo="DIMENSIONAL",
                        descripcion=f"Desviación dimensional de {obs.desviacion}",
                        gravedad=gravedad
                    )
                )
        return defectos

    def _calcular_gravedad(self, obs):
        exceso = obs.desviacion / obs.tolerancia
        if exceso <= 1.25:
            return 1
        if exceso <= 1.5:
            return 2
        if exceso <= 2:
            return 3
        if exceso <= 3:
            return 4
        return 5

