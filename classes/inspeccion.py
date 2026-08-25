
class Inspeccion:
    def __init__(self, id, muestra, profesional, equipo, procedimiento, fecha):
        self._id = id
        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._defectos = []
        self._cerrada = False

    def get_id(self):
        return self._id

    def get_muestra_id(self):
        return self._muestra.get_id()

    def get_profesional_id(self):
        return self._profesional.get_id()

    def get_equipo_id(self):
        return self._equipo.get_id()

    def get_procedimiento_id(self):
        return self._procedimiento.get_id()

    def get_fecha(self):
        return self._fecha

    def get_defectos(self):
        return self._defectos

    def ejecutar(self, observaciones):
        pass

    def cerrar(self):
        pass