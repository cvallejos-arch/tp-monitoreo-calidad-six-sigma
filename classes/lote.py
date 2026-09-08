from classes.muestra import Muestra
from classes.estado_lote import EstadoLote
from classes.validacion import validar_cantidad
import uuid

class Lote:
    def __init__(self, _nombre_componentes, cantidad_fabricada):
        self._id = uuid.uuid4()
        self._nombre_componentes = _nombre_componentes

        #validar atributos y definirlos
        if validar_cantidad(self._cantidad_fabricada):
            self._cantidad_fabricada = cantidad_fabricada
    
        self._estado = EstadoLote.EN_PRODUCCION
        self._muestras = []

    def get_id(self):
        return self._id

    def get_nombre_lote(self):
        return self._nombre_componentes

    def get_cantidad_fabricada(self):
        return self._cantidad_fabricada

    def get_estado(self):
        return self._estado

    def get_muestras(self):
        return self._muestras

    def agregar_muestra(self, muestra):
        if isinstance(muestra, Muestra):
            self._muestras.append(muestra)

    def decidir(self):
        pass

    def porcentaje_no_conforme(self):
        pass

    def todas_cerradas(self):
        pass

    def total_defectos_criticos(self):
        pass

    def conteo_por_tipo(self):
        pass