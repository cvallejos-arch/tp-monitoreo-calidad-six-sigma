from lote import Lote
from procedimiento import Procedimiento
from inspeccion import Inspeccion
from profesional import Profesional
from equipo import Equipo
from muestra import Muestra


class Empresa:
    def __init__(self):
        self._registros = {
            "lotes": {},
            "muestras": {},
            "profesionales": {},
            "equipos": {},
            "procedimientos": {},
            "inspecciones": {}
        }

    def crear_registrar_lote(self, nombre_componentes, cantidad_fabricada):
        lote = Lote(nombre_componentes, cantidad_fabricada)
        self._registros["lotes"][lote.id] = lote
        return lote

    def crear_registrar_muestra(self, cantidad):
        muestra = Muestra(cantidad)
        self._registros["muestras"][muestra.id] = muestra
        return muestra

    def crear_registrar_profesional(self, nombre):
        profesional = Profesional(nombre)
        self._registros["profesionales"][profesional.id] = profesional
        return profesional

    def crear_registrar_equipo(self, id, categoria, fecha_calibracion):
        equipo = Equipo(id, categoria, fecha_calibracion)
        self._registros["equipos"][equipo.id] = equipo
        return equipo

    def crear_registrar_procedimiento(
        self,
        limite_gravedad_acumulada,
        categoria_equipo_requerida,
        certificacion_requerida=None
    ):
        procedimiento = Procedimiento(
            limite_gravedad_acumulada,
            categoria_equipo_requerida,
            certificacion_requerida
        )

        self._registros["procedimientos"][procedimiento.id] = procedimiento
        return procedimiento

    def crear_registrar_inspeccion(
        self,
        muestra,
        profesional,
        equipo,
        procedimiento,
        fecha
    ):
        inspeccion = Inspeccion(
            muestra,
            profesional,
            equipo,
            procedimiento,
            fecha
        )

        self._registros["inspecciones"][inspeccion.id] = inspeccion
        return inspeccion

    def lanzar_inspeccion(
        self,
        muestra,
        profesional,
        equipo,
        procedimiento,
        fecha
    ):
        pass