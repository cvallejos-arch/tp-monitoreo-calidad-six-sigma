from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.validacion import validar_cantidad, validar_texto
from classes.excepciones import TransicionIlegalError

import uuid


class Lote:
    def __init__(self, nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = validar_texto(
            nombre_componentes,
            "nombre_componentes"
        )
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

    def crear_muestra(self, cantidad):
        """Crea una muestra que pertenece a este lote (composición).
        Valida que la capacidad no se exceda."""
        validar_cantidad(cantidad)

        # Transformamos cada muestra en su cantidad y luego las sumamos.
        capacidad_usada = sum(
            map(lambda m: m.cantidad, self._muestras.values())
        )

        if capacidad_usada + cantidad > self._cantidad_fabricada:
            raise TransicionIlegalError(
                f"No se puede crear una muestra de {cantidad} unidades: "
                f"la suma ({capacidad_usada + cantidad}) excede la cantidad "
                f"fabricada ({self._cantidad_fabricada}).",
                lote_id=self._id,
                capacidad_usada=capacidad_usada,
                cantidad_solicitada=cantidad,
                cantidad_fabricada=self._cantidad_fabricada
            )

        muestra = Muestra(cantidad, self._id)
        self._muestras[muestra.id] = muestra
        return muestra

    def _muestras_cerradas(self):
        """Filtra las muestras que se encuentran en un estado final."""
        estados_finales = (
            EstadoMuestra.CONFORME,
            EstadoMuestra.NO_CONFORME
        )

        return filter(
            lambda m: m.estado in estados_finales,
            self._muestras.values()
        )

    def decidir(self):
        """Decide el estado del lote basado en el porcentaje de muestras
        no conformes. RECHAZADO si > 5%, APROBADO si <= 5%.
        La decisión es final."""
        if self._estado != EstadoLote.EN_PRODUCCION:
            raise TransicionIlegalError(
                f"El lote '{self._id}' ya está decidido "
                f"({self._estado.value})."
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

        # Seleccionamos únicamente las muestras no conformes.
        no_conformes = filter(
            lambda m: m.estado == EstadoMuestra.NO_CONFORME,
            self._muestras.values()
        )

        # Transformamos cada muestra filtrada en 1 para poder contarlas.
        cantidad_no_conformes = sum(
            map(lambda m: 1, no_conformes)
        )

        return cantidad_no_conformes / total_muestras * 100

    def todas_cerradas(self):
        """Verifica si todas las muestras están en un estado final."""
        estados_finales = (
            EstadoMuestra.CONFORME,
            EstadoMuestra.NO_CONFORME
        )

        return all(
            map(
                lambda m: m.estado in estados_finales,
                self._muestras.values()
            )
        )

    def total_defectos_criticos(self):
        """Cuenta el total de defectos críticos de las muestras cerradas."""

        # Primero se filtran las muestras cerradas.
        # Luego cada muestra se transforma en su cantidad de defectos críticos.
        # Finalmente se suman esas cantidades.
        return sum(
            map(
                lambda m: sum(
                    map(
                        lambda d: 1 if d.es_critico() else 0,
                        m.defectos
                    )
                ),
                self._muestras_cerradas()
            )
        )

    def conteo_por_tipo(self):
        """Retorna un dict {tipo: cantidad} con los defectos
        encontrados en muestras cerradas."""
        conteo = {}

        # Se recorren únicamente las muestras cerradas.
        for muestra in self._muestras_cerradas():
            for defecto in muestra.defectos:
                conteo[defecto.tipo] = conteo.get(defecto.tipo, 0) + 1

        return conteo

    def __repr__(self):
        return (
            f"Lote(id={self._id}, "
            f"nombre_componentes='{self._nombre_componentes}', "
            f"cantidad_fabricada={self._cantidad_fabricada}, "
            f"estado={self._estado.value}, "
            f"muestras={len(self._muestras)})"
        )