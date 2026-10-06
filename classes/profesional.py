import uuid

from classes.excepciones import DatosInvalidosError
from classes.certificacion import Certificacion
from classes.validacion import validar_texto


class Profesional:
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
        """Retorna las certificaciones vigentes en la fecha indicada."""
        return tuple(
            filter(
                lambda cert: cert.es_vigente(fecha),
                self._certificaciones.values()
            )
        )

    def __repr__(self):
        certificaciones = ", ".join(
            f"{nombre}: {cert}"
            for nombre, cert in self._certificaciones.items()
        )

        return (
            f"Profesional(id={self._id}, "
            f"nombre='{self._nombre}', "
            f"certificaciones={{ {certificaciones} }})"
        )