class Procedimiento:
    def __init__(self, id, limite_gravedad_acumulada, categoria_equipo_requerida, certificacion_requerida=None):
        self._id = id
        self._limite_gravedad_acumulada = limite_gravedad_acumulada
        self._categoria_equipo_requerida = categoria_equipo_requerida
        self._certificacion_requerida = certificacion_requerida

    def get_id(self):
        return self._id

    def get_limite_gravedad_acumulada(self):
        return self._limite_gravedad_acumulada

    def get_categoria_equipo_requerida(self):
        return self._categoria_equipo_requerida

    def get_certificacion_requerida(self):
        return self._certificacion_requerida

    def evaluar(self, observaciones):
        raise NotImplementedError("Se crea en los subclases")
        
        


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


class ProcedimientoVisual(Procedimiento):
    def evaluar(self, observaciones):
        defectos = []
        for obs in observaciones:
            if obs.es_defecto:
                defectos.append(Defecto(tipo="VISUAL", descripcion=obs.detalle, gravedad=obs.gravedad))
        return defectos
        

class test(Procedimiento):
    pass

a = test()
a.evaluar()