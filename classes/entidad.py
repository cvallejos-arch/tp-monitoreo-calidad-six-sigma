class Entidad:
    """Clase base de las entidades del dominio que tienen un id propio (uuid4):
    Lote, Muestra, Profesional, Equipo, Procedimiento, Inspeccion y Reporte.

    La identidad de una entidad es su id, no su posición en memoria: un lote
    cargado con pickle o un reporte cargado desde JSON es OTRO objeto, pero
    representa la MISMA entidad, así que tiene que ser igual al original.

    Si una clase define __eq__, Python anula el __hash__ heredado (queda en None)
    y sus objetos ya no se pueden guardar en un set ni usar como clave de un dict.
    Por eso se definen los dos juntos, sobre un atributo INMUTABLE: el id nunca
    cambia durante la vida del objeto. Se cumple la regla de la cátedra:
    a == b  implica  hash(a) == hash(b)."""

    def __eq__(self, otro):
        """Dos entidades son iguales si son del mismo tipo y tienen el mismo id."""
        if not isinstance(otro, Entidad):
            return NotImplemented
        return type(self) is type(otro) and self._id == otro._id

    def __hash__(self):
        return hash(self._id)
