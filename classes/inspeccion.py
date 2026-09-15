from datetime import date

from classes.estado_muestra import EstadoMuestra
from classes.excepciones import (
    CertificacionNoVigenteError,
    DatosInvalidosError,
    EquipoNoAptoError,
    TransicionIlegalError,
    InspeccionInvalidaError,
)


import uuid

class Inspeccion:
    def __init__(self, muestra, profesional, equipo, procedimiento, fecha):
        self._id = uuid.uuid4()

        if not isinstance(fecha, date):
            raise DatosInvalidosError(
                "La fecha de la inspección debe ser un objeto de tipo 'date'."
            )

        if muestra.estado != EstadoMuestra.PENDIENTE:
            raise TransicionIlegalError(
                "La muestra '" + muestra.id + "' no está en estado PENDIENTE."
            )

        cert_requerida = procedimiento.get_certificacion_requerida()
        if cert_requerida is not None and not profesional.tiene_certificacion(cert_requerida, fecha):
            raise CertificacionNoVigenteError(
                "El profesional '" + profesional.get_id() +
                "' no tiene la certificación requerida '" + cert_requerida +
                "' vigente a la fecha" + str(fecha) + "."
            )

        if not equipo.es_compatible_con_procedimiento(procedimiento.categoria_equipo_requerida):
            raise EquipoNoAptoError(
                "El equipo '" + equipo.get_id() +
                "' no es compatible con el procedimiento '" + procedimiento.get_id() + "'."
            )

        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._defectos = []
        self._cerrada = False

    @property
    def id(self):
        return self._id

    @property
    def muestra_id(self):
        return self._muestra.get_id()

    @property
    def profesional_id(self):
        return self._profesional.get_id()

    @property
    def equipo_id(self):
        return self._equipo.get_id()

    @property
    def procedimiento_id(self):
        return self._procedimiento.get_id()

    @property
    def fecha(self):
        return self._fecha

    @property
    def defectos(self):
        return self._defectos

    def ejecutar(self, observaciones):
        pass

    def cerrar(self):
        pass