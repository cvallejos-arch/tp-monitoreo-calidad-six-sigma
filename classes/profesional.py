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
        """Retorna una copia del dict de certificaciones."""
        return dict(self._certificaciones)

    def agregar_certificacion(self, cert):
        """Agrega una certificación al profesional. Usa dict para acceso por nombre."""
        if not isinstance(cert, Certificacion):
            raise DatosInvalidosError(
                f"El objeto '{cert}' no es una instancia de la clase 'Certificacion'."
            )
        self._certificaciones[cert.nombre] = cert

    def tiene_certificacion_vigente(self, nombre, fecha):
        """Verifica si el profesional tiene una certificación vigente con el nombre dado
        en la fecha indicada. Usa dict.get() para acceso eficiente."""
        cert = self._certificaciones.get(nombre)
        if cert is None:
            return False
        return cert.es_vigente(fecha)

    def __repr__(self):
        return (
            f"Profesional(id={self._id}, nombre='{self._nombre}', "
            f"certificaciones={list(self._certificaciones.keys())})"
        )
