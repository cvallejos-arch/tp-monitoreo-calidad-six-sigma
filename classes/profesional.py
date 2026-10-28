import uuid

from classes.entidad import Entidad
from classes.excepciones import DatosInvalidosError
from classes.certificacion import Certificacion
from classes.validacion import validar_texto


class Profesional(Entidad):
    def __init__(self, nombre):
        self._id = uuid.uuid4()
        self._nombre = validar_texto(nombre, "nombre")
        self._certificaciones = {}  # dict {nombre_cert: Certificacion}

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def certificaciones(self):
        """Retorna una copia del diccionario de certificaciones."""
        return dict(self._certificaciones)

    def agregar_certificacion(self, cert):
        """Agrega una certificación al profesional."""
        if not isinstance(cert, Certificacion):
            raise DatosInvalidosError(
                f"El objeto '{cert}' no es una instancia de la clase "
                f"'Certificacion'."
            )

        self._certificaciones[cert.nombre] = cert

    def tiene_certificacion_vigente(self, nombre, fecha):
        """Verifica si el profesional tiene una certificación vigente
        con el nombre indicado en la fecha dada."""
        cert = self._certificaciones.get(nombre)

        if cert is None:
            return False

        return cert.es_vigente(fecha)

    def certificaciones_vigentes(self, fecha):
        """Retorna las certificaciones vigentes en la fecha indicada, de la que
        vence primero a la que vence última (sorted con key)."""
        vigentes = filter(lambda cert: cert.es_vigente(fecha), self._certificaciones.values())
        return tuple(sorted(vigentes, key=lambda cert: cert.fecha_fin))

    def __repr__(self):
        # Se recorre el dict con .items(): cada par es (nombre, certificacion).
        certificaciones = ", ".join(
            map(
                lambda par: f"{par[0]}: {par[1]}",
                self._certificaciones.items()
            )
        )

        return (
            f"Profesional(id={self._id}, "
            f"nombre='{self._nombre}', "
            f"certificaciones={{{certificaciones}}})"
        )