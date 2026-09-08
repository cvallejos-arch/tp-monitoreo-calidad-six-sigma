from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad
from classes.excepciones import TransicionIlegalError
from classes.reporte import Reporte
import uuid

class Muestra:
    def __init__(self, cantidad):
        self._id = uuid.uuid4()
        self._cantidad = validar_cantidad(cantidad)
        self._estado = EstadoMuestra.PENDIENTE
        self._defectos = []
        self._lote_id = None
        self._inspeccion = None
        self._reporte = None

    @property
    def get_id(self):
        return self._id
    
    @property
    def get_cantidad(self):
        return self._cantidad
    
    @property
    def get_estado(self):
        return self._estado
    
    @property
    def get_defectos(self):
        return self._defectos
    
    @property
    def get_lote_id(self):
        return self._lote_id

    @property
    def inspeccion(self):
        return self._inspeccion

    @property
    def get_reporte(self):
        return self._reporte

#--- Gestion de la apartenencia al lote ---

    def asignar_lote(self, lote_id):
        if self._lote_id is not None:
            raise TransicionIlegalError(
                "La muestra '" + self._id + "' appartient déjà au lote "
                "'" + self._lote_id + "' et ne peut pas être déplacée vers "
                "'" + lote_id + "'."
            )
        self._lote_id = lote_id

    def iniciar_inspeccion(self):
        """ PENDIENTE a EN_INSPECCION"""
        if self._estado != EstadoMuestra.PENDIENTE:
            raise TransicionIlegalError(
                "No se pudo iniciar la inspección: la muestra '" + self._id + 
                "' está en estado" + self._estado.value + ", se espera PENDENTIE."
            )
        self._estado = EstadoMuestra.EN_INSPECCION
        

    def agregar_defecto(self, defecto):
        """ anadir un defecto"""
        if self._estado != EstadoMuestra.EN_INSPECCION:
            raise TransicionIlegalError(
                "No se pudo anadir un defecto: la muestra '" + self._id + 
                "' está en estado" + self._estado.value + ", se espera EN_INSPECCION."
            )
        self._defectos.append(defecto)

    def cerrar(self, limite_gravedad):
        if self._estado != EstadoMuestra.EN_INSPECCION:
            raise TransicionIlegalError(
                "No se pudo cerrar la muestra '" + self._id + 
                "' está en estado" + self._estado.value + ", se espera EN_INSPECCION."
            )

        if self.tiene_critico() or self.suma_gravedades() > limite_gravedad:
            self._estado = EstadoMuestra.NO_CONFORME
        else:
            self._estado = EstadoMuestra.CONFORME

        if self._estado == EstadoMuestra.NO_CONFORME:
            self._reporte = Reporte(
                self._id,
                self._lote_id,
                self.inspeccion.profesional_id,
                self._inspeccion.fecha,
                self._defectos
            )


    def suma_gravedades(self):
        total=0
        for d in self._defectos:
            total = total + d.gravedad
        return total


    def tiene_critico(self):
        for d in self._defectos:
            if d.es_critico():
                return True
        return False 

    def __repr__(self):
        return (
            "Muestra(id=" + repr(self._id) + ", cantidad=" + str(self._cantidad) + ", "
            "estado=" + self._estado.value + ", defectos=" + str(len(self._defectos)) + ", "
            "lote_id=" + repr(self._lote_id) + ")"
        )   
            
