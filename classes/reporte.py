import uuid


class Reporte:

    def __init__(self, muestra_id, lote_id, profesional_id, fecha, defectos,
                 historial_estados=()):
        self._id = uuid.uuid4()
        self._muestra_id = muestra_id
        self._lote_id = lote_id
        self._profesional_id = profesional_id
        self._fecha = fecha
        # Copia inmutable usando map() para copiar cada defecto
        self._defectos = tuple(map(lambda d: d.copia(), defectos))
        # Recorrido de estados de la muestra, del más antiguo al más nuevo
        self._historial_estados = tuple(historial_estados)

    @property
    def id(self):
        return self._id

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

    @property
    def historial_estados(self):
        return self._historial_estados

    def __repr__(self):
        return (
            f"Reporte(id={self._id}, muestra_id={self._muestra_id}, "
            f"lote_id={self._lote_id}, profesional_id={self._profesional_id}, "
            f"fecha={self._fecha}, defectos={len(self._defectos)})"
        )
