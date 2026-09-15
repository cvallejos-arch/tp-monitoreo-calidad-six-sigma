from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad
from classes.excepciones import DatosInvalidosError, TransicionIlegalError

import uuid

class Lote:
    def __init__(self, nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = nombre_componentes

        #validar atributos y definirlos
        if validar_cantidad(self._cantidad_fabricada):
            self._cantidad_fabricada = cantidad_fabricada
    
        self._estado = EstadoLote.EN_PRODUCCION
        self._muestras = []

    @property
    def id(self):
        return self._id

    @property
    def nombre_lote(self):
        return self._nombre_componentes

    @property
    def cantidad_fabricada(self):
        return self._cantidad_fabricada

    @property
    def estado(self):
        return self._estado

    @property
    def muestras(self):
        return tuple(self._muestras.values())

    def agregar_muestra(self, muestra):
        if muestra.id in self._muestras:
            raise DatosInvalidosError(
                "La muestra '" + muestra.id + "' exista en el lote '" + self._id + "'."
            )
        capacidad_usando = 0
        for m in self._muestras.values():
            capacidad_usando += m.cantidad

        if capacidad_usando + muestra.cantidad > self._cantidad_fabricada:
            raise TransicionIlegalError(
                "No se puede agregar la muestra '" + muestra.id +
                "' (cantidad=" + str(muestra.cantidad) + ") : el sum de las cantidades "
                "(" + str(capacidad_usando + muestra.cantidad) + ") excede la cantidad"
                "fabricada (" + str(self._cantidad_fabricada) + ")."
            )
        
        muestra.asignar_lote(self._id)

        self._muestras[muestra.id] = muestra

        
    def decidir(self):
        if self._estado != EstadoLote.EN_PRODUCCION:
            raise TransicionIlegalError(
                "El lote  '" + self._id + "' : esta decidido ("
                + self._estado.value + ")."
            )

        if not self._muestras:
            raise TransicionIlegalError(
                "El lote '" + self._id + "' : no tiene muestras."
            )
        if not self.todas_cerradas():
            raise TransicionIlegalError(
                "El lote '" + self._id + "' : no todas las muestras están cerradas."
            )

        if self.porcentaje_no_conforme() > 5:
            self._estado = EstadoLote.RECHAZADO
        else:
            self._estado = EstadoLote.APROBADO
        return self._estado


    def porcentaje_no_conforme(self):
        total_muestras = len(self._muestras)
        if total_muestras == 0:
            return 0
        no_conforme_count = 0
        for m in self._muestras.values():
            if m.estado == EstadoMuestra.NO_CONFORME:
                no_conforme_count += 1
        return no_conforme_count / total_muestras * 100
        
    def todas_cerradas(self):
        for m in self._muestras.values():
            if m.estado not in (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME):
                return False
        return True

    def total_defectos_criticos(self):
        toal = 0
        for m in self._muestras.values():
            if m.estado in (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME):
                for d in m.defectos:
                    if d.es_critico():
                        toal += 1
        return toal

    def conteo_por_tipo(self):
        conteo = {}
        for m in self._muestras.values():
            if m.estado in (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME):
                for d in m.defectos:
                    if d.tipo in conteo:
                        conteo[d.tipo] += 1
                    else:
                        conteo[d.tipo] = 1
        return conteo

    def __repr__(self):
        return (
            "Lote(id=" + repr(self._id) + ", nombre_componentes=" + repr(self._nombre_componentes) + ", "
            "cantidad_fabricada=" + str(self._cantidad_fabricada) + ", "
            "estado=" + self._estado.value + ", muestras=" + str(len(self._muestras)) + ")"
        )