class Reporte:
    def __init__(self, muestra_id, lote_id, profesional_id, fecha, defectos):
        self._muestra_id = muestra_id
        self._lote_id = lote_id
        self._profesional_id = profesional_id
        self._fecha = fecha
        self._defectos = defectos

    def get_muestra_id(self):
        return self._muestra_id

    def get_lote_id(self):
        return self._lote_id

    def get_profesional_id(self):
        return self._profesional_id

    def get_fecha(self):
        return self._fecha

    def get_defectos(self):
        return self._defectos
