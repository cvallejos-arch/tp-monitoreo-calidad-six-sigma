import uuid
from classes.excepciones import DatoInvalidoException
from classes.certificacion import Certificacion
from classes.validacion import validar_texto

class Profesional:
    def __init__(self, nombre):
        validar_texto(nombre)
        self._id = uuid.uuid4()
        self._nombre = nombre
        self._certificaciones = [] # {}?  "CONTROL_DIMENSIONAL": certificacion1,

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def certificaciones(self):
        return tuple(self._certificaciones)

    def agregar_certificacion(self, cert):
        if not isinstance(cert, Certificacion):
            raise DatoInvalidoException(
                "El objeto '" + str(cert) + "' no es una instancia de la clase 'Certificacion'."
            )
        self._certificaciones.append(cert)

    def tiene_certificacion_vigente(self, nombre, fecha):
        for cert in self._certificaciones:
            if cert.nombre == nombre and cert.es_vigente(fecha):
                return True
        return False
    
    def __repr__(self):
        return (
            "Profesional(id=" + str(self._id) +
            ", nombre=" + self._nombre +
            ", certificaciones=" + str(self._certificaciones) +
            ")"
        )
