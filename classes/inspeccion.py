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

        # Validar estado de la muestra
        if muestra.estado != EstadoMuestra.PENDIENTE:
            raise TransicionIlegalError(
                f"La muestra '{muestra.id}' no está en estado PENDIENTE."
            )

        # Validar certificación del profesional
        cert_requerida = procedimiento.certificacion_requerida
        if cert_requerida is not None:
            if not profesional.tiene_certificacion_vigente(cert_requerida, fecha):
                raise CertificacionNoVigenteError(
                    f"El profesional '{profesional.id}' no tiene la certificación "
                    f"requerida '{cert_requerida}' vigente a la fecha {fecha}."
                )

        # Validar compatibilidad del equipo
        if not equipo.es_compatible(procedimiento.categoria_equipo_requerida):
            raise EquipoNoAptoError(
                f"El equipo '{equipo.id}' (categoría '{equipo.categoria}') "
                f"no es compatible con el procedimiento '{procedimiento.id}' "
                f"(requiere '{procedimiento.categoria_equipo_requerida}')."
            )

        # Validar calibración del equipo
        if not equipo.esta_calibrado(fecha):
            raise EquipoNoAptoError(
                f"El equipo '{equipo.id}' no está calibrado a la fecha {fecha}."
            )

        # Iniciar la inspección (transición PENDIENTE → EN_INSPECCION)
        muestra.iniciar_inspeccion()

        # Guardar el contexto de la inspección (inmutable durante la ejecución)
        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._cerrada = False

        # Asignar inspección a la muestra (encapsulación correcta)
        muestra.asignar_inspeccion(self)

    @property
    def id(self):
        return self._id

    @property
    def muestra_id(self):
        return self._muestra.id

    @property
    def profesional_id(self):
        return self._profesional.id

    @property
    def equipo_id(self):
        return self._equipo.id

    @property
    def procedimiento_id(self):
        return self._procedimiento.id

    @property
    def fecha(self):
        return self._fecha

    @property
    def cerrada(self):
        return self._cerrada

    @property
    def defectos(self):
        return self._muestra.defectos

    def ejecutar(self, observaciones):
        """Ejecuta el procedimiento con las observaciones dadas.
        El procedimiento evalúa polimórficamente y genera defectos."""
        if self._cerrada:
            raise InspeccionInvalidaError(
                f"La inspección '{self._id}' ya ha sido cerrada y no puede "
                f"ser ejecutada nuevamente."
            )

        defectos = self._procedimiento.evaluar(observaciones)
        for d in defectos:
            self._muestra.agregar_defecto(d)
        return defectos

    def cerrar(self):
        """Cierra la inspección y determina la conformidad de la muestra."""
        if self._cerrada:
            raise InspeccionInvalidaError(
                f"La inspección '{self._id}' ya ha sido cerrada."
            )
        self._cerrada = True
        return self._muestra.cerrar(self._procedimiento.limite_gravedad_acumulada)

    def __repr__(self):
        return (
            f"Inspeccion(id={self._id}, muestra_id={self._muestra.id}, "
            f"profesional_id={self._profesional.id}, equipo_id={self._equipo.id}, "
            f"procedimiento_id={self._procedimiento.id}, fecha={self._fecha}, "
            f"cerrada={self._cerrada})"
        )
