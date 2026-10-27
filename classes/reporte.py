import uuid
from datetime import date

from classes.defecto import Defecto
from classes.estado_muestra import EstadoMuestra


class Reporte:

    def __init__(self, muestra_id, lote_id, profesional_id, fecha, defectos,
                 historial_estados=(), reporte_id=None):
        # reporte_id solo se indica al reconstruir un reporte guardado (from_dict);
        # un reporte nuevo genera su propio id.
        self._id = reporte_id if reporte_id is not None else uuid.uuid4()
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

    @property
    def gravedad_maxima(self):
        """La gravedad más alta entre sus defectos (5 = hay un crítico)."""
        return max(map(lambda d: d.gravedad, self._defectos), default=0)

    @property
    def suma_gravedades(self):
        return sum(map(lambda d: d.gravedad, self._defectos))

    # --- Serialización JSON ---

    def to_dict(self):
        """Retorna el reporte como dict con tipos que JSON entiende:
        UUID -> str, date -> 'AAAA-MM-DD', Enum -> su valor, tupla -> lista.
        Las claves coinciden con los parámetros del constructor."""
        return {
            "reporte_id": str(self._id),
            "muestra_id": str(self._muestra_id),
            "lote_id": str(self._lote_id),
            "profesional_id": str(self._profesional_id),
            "fecha": self._fecha.isoformat(),
            "historial_estados": list(map(lambda e: e.value, self._historial_estados)),
            "defectos": list(map(lambda d: d.to_dict(), self._defectos))
        }

    @staticmethod
    def from_dict(data):
        """Reconstruye un reporte desde un dict generado por to_dict(): convierte
        los textos de vuelta a date, EstadoMuestra y Defecto, y crea Reporte(**datos)."""
        datos = dict(data)                  # copia: no modifica el dict recibido
        datos["fecha"] = date.fromisoformat(datos["fecha"])
        datos["historial_estados"] = tuple(map(EstadoMuestra, datos["historial_estados"]))
        datos["defectos"] = list(map(Defecto.from_dict, datos["defectos"]))
        return Reporte(**datos)

    def __repr__(self):
        return (
            f"Reporte(id={self._id}, muestra_id={self._muestra_id}, "
            f"lote_id={self._lote_id}, profesional_id={self._profesional_id}, "
            f"fecha={self._fecha}, defectos={len(self._defectos)})"
        )
