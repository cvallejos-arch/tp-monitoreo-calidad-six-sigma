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
                "El profesional '" + profesional.id() +
                "' no tiene la certificación requerida '" + cert_requerida +
                "' vigente a la fecha" + str(fecha) + "."
            )

        if not equipo.es_compatible_con_procedimiento(procedimiento.categoria_equipo_requerida):
            raise EquipoNoAptoError(
                "El equipo '" + equipo.id +
                "' no es compatible con el procedimiento '" + procedimiento.id + "'."
            )

        if not equipo.esta_calibrado(fecha):
            raise EquipoNoAptoError(
                "El equipo '" + equipo.id +
                "' no está calibrado a la fecha " + str(fecha) + "."
            )
        muestra.iniciar_inspeccion()


        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        muestra._inspeccion = self
        self._cerrada = False

    @property
    def id(self):
        return self._id

    @property
    def muestra_id(self):
        return self._muestra.id()

    @property
    def profesional_id(self):
        return self._profesional.id()

    @property
    def equipo_id(self):
        return self._equipo.id()

    @property
    def procedimiento_id(self):
        return self._procedimiento.id()

    @property
    def fecha(self):
        return self._fecha

    @property
    def defectos(self):
        return self._muestra.defectos

    def ejecutar(self, observaciones):
        if self._cerrada:
            raise InspeccionInvalidaError(
                "La inspección '" + self._id +
                "' ya ha sido cerrada y no puede ser ejecutada nuevamente."
            )

        defectos = self._procedimiento.evaluar(observaciones)
        for d in defectos:
            self._muestra.agregar_defecto(d)
        return defectos

    def cerrar(self):
        if self.cerrada:
            raise InspeccionInvalidaError(
                "La inspección '" + self._id +
                "' ya ha sido cerrada y no puede ser cerrada nuevamente."
            )
        self._cerrada = True
        return self._muestra.cerrar(self._procedimiento.limite_gravedad_acumulada)

    def __repr__(self):
        return (
            "Inspeccion(id=" + str(self._id) +
            ", muestra_id=" + str(self._muestra.id()) +
            ", profesional_id=" + str(self._profesional.id()) +
            ", equipo_id=" + str(self._equipo.id()) +
            ", procedimiento_id=" + str(self._procedimiento.id()) +
            ", fecha=" + str(self._fecha) +
            ", cerrada=" + str(self._cerrada) +
            ")"
        )

