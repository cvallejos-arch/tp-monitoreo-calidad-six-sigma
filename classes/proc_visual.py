from classes.procedimiento import Procedimiento
from classes.defecto import Defecto


class ProcedimientoVisual(Procedimiento):
    def evaluar(self, observaciones):
        defectos = []
        for obs in observaciones:
            if obs.es_defecto:
                defectos.append(Defecto(tipo="VISUAL", descripcion=obs.detalle, gravedad=obs.gravedad))
        return defectos

