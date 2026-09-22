import uuid

class Reporte:
    def __init__(self, muestra_id, lote_id, profesional_id, fecha, defectos):
        
        self._id = uuid.uuid4()
        self._muestra_id = muestra_id
        self._lote_id = lote_id
        self._profesional_id = profesional_id
        self._fecha = fecha
        self._defectos = tuple(map(lambda d: d.copia(), defectos))

    @property
    def muestra_id(self):
        return self._muestra_id

    @property
    def lote_id(self):
        return self._lote_id

    @property
    def profesional_id(self):
        return self._profesional_id

    @property
    def fecha(self):
        return self._fecha

    @property
    def defectos(self):
        return self._defectos

def __repr__(self):
        return (
            "Reporte(id=" + str(self._id) +
            ", muestra_id=" + str(self._muestra_id) +
            ", lote_id=" + str(self._lote_id) +
            ", profesional_id=" + str(self._profesional_id) +
            ", fecha=" + str(self._fecha) +
            ", defectos=" + str(self._defectos) +
            ")"
        )
