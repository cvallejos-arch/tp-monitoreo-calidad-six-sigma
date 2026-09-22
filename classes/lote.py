from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad, validar_texto
from classes.excepciones import DatosInvalidosError, TransicionIlegalError

import uuid


class Lote:
    def __init__(self, nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = validar_texto(nombre_componentes, "nombre_componentes")
        self._cantidad_fabricada = validar_cantidad(cantidad_fabricada)
        self._estado = EstadoLote.EN_PRODUCCION
        self._muestras = {}  # dict {muestra.id: muestra}

    @property
    def id(self):
        return self._id

    @property
    def nombre_componentes(self):
        return self._nombre_componentes

    @property
    def cantidad_fabricada(self):
        return self._cantidad_fabricada

    @property
    def estado(self):
        return self._estado

    @property
    def muestras(self):
        """Retorna una tupla inmutable de las muestras del lote."""
        return tuple(self._muestras.values())

    def agregar_muestra(self, muestra):
        """Agrega una muestra al lote con las validaciones de negocio."""
        if muestra.id in self._muestras:
            raise DatosInvalidosError(
                f"La muestra '{muestra.id}' ya existe en el lote '{self._id}'."
            )

        # Calcular capacidad utilizada usando sum() + map()
        capacidad_usada = sum(map(lambda m: m.cantidad, self._muestras.values()))

        if capacidad_usada + muestra.cantidad > self._cantidad_fabricada:
            raise TransicionIlegalError(
                f"No se puede agregar la muestra '{muestra.id}' "
                f"(cantidad={muestra.cantidad}): la suma de cantidades "
                f"({capacidad_usada + muestra.cantidad}) excede la cantidad "
                f"fabricada ({self._cantidad_fabricada})."
            )

        muestra.asignar_lote(self._id)
        self._muestras[muestra.id] = muestra

    def decidir(self):
        """Decide el estado del lote basado en el porcentaje de muestras no conformes.
        RECHAZADO si > 5%, APROBADO si <= 5%. La decisión es final."""
        if self._estado != EstadoLote.EN_PRODUCCION:
            raise TransicionIlegalError(
                f"El lote '{self._id}' ya está decidido ({self._estado.value})."
            )

        if not self._muestras:
            raise TransicionIlegalError(
                f"El lote '{self._id}' no tiene muestras."
            )

        if not self.todas_cerradas():
            raise TransicionIlegalError(
                f"El lote '{self._id}': no todas las muestras están cerradas."
            )

        if self.porcentaje_no_conforme() > 5:
            self._estado = EstadoLote.RECHAZADO
        else:
            self._estado = EstadoLote.APROBADO
        return self._estado

    def porcentaje_no_conforme(self):
        """Calcula el porcentaje de muestras no conformes sin redondear.
        Consulta sin efectos secundarios."""
        total_muestras = len(self._muestras)
        if total_muestras == 0:
            return 0
        # Contar no conformes usando sum() + map()
        no_conforme_count = sum(
            map(lambda m: 1 if m.estado == EstadoMuestra.NO_CONFORME else 0,
                self._muestras.values())
        )
        return no_conforme_count / total_muestras * 100

    def todas_cerradas(self):
        """Verifica si todas las muestras están en un estado final."""
        estados_finales = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)
        return all(map(lambda m: m.estado in estados_finales, self._muestras.values()))

    def total_defectos_criticos(self):
        """Cuenta el total de defectos críticos en muestras cerradas.
        Consulta sin efectos secundarios."""
        total = 0
        estados_finales = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)
        for m in self._muestras.values():
            if m.estado in estados_finales:
                # Usar sum() + map() para contar críticos por muestra
                total += sum(map(lambda d: 1 if d.es_critico() else 0, m.defectos))
        return total

    def conteo_por_tipo(self):
        """Retorna un dict {tipo: cantidad} de defectos en muestras cerradas.
        Usa dict.get() para acceso seguro. Consulta sin efectos secundarios."""
        conteo = {}
        estados_finales = (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)
        for m in self._muestras.values():
            if m.estado in estados_finales:
                for d in m.defectos:
                    conteo[d.tipo] = conteo.get(d.tipo, 0) + 1
        return conteo

    def __repr__(self):
        return (
            f"Lote(id={self._id}, nombre_componentes='{self._nombre_componentes}', "
            f"cantidad_fabricada={self._cantidad_fabricada}, "
            f"estado={self._estado.value}, muestras={len(self._muestras)})"
        )