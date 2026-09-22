from classes.lote import Lote
from classes.procedimiento import Procedimiento
from classes.inspeccion import Inspeccion
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.muestra import Muestra


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
        """Crea y registra un lote en el sistema."""
        lote = Lote(nombre_componentes, cantidad_fabricada)
        self._registros["lotes"][lote.id] = lote
        return lote

    def crear_registrar_muestra(self, cantidad):
        """Crea y registra una muestra en el sistema."""
        muestra = Muestra(cantidad)
        self._registros["muestras"][muestra.id] = muestra
        return muestra

    def crear_registrar_profesional(self, nombre):
        """Crea y registra un profesional en el sistema."""
        profesional = Profesional(nombre)
        self._registros["profesionales"][profesional.id] = profesional
        return profesional

    def crear_registrar_equipo(self, categoria, fecha_calibracion):
        """Crea y registra un equipo en el sistema."""
        equipo = Equipo(categoria, fecha_calibracion)
        self._registros["equipos"][equipo.id] = equipo
        return equipo

    def crear_registrar_procedimiento(self, tipo_procedimiento, **kwargs):

        procedimiento = tipo_procedimiento(**kwargs)
        self._registros["procedimientos"][procedimiento.id] = procedimiento
        return procedimiento

    def lanzar_inspeccion(self, muestra, profesional, equipo, procedimiento, fecha):
        """Crea y registra una inspección en el sistema."""
        inspeccion = Inspeccion(
            muestra=muestra,
            profesional=profesional,
            equipo=equipo,
            procedimiento=procedimiento,
            fecha=fecha
        )
        self._registros["inspecciones"][inspeccion.id] = inspeccion
        return inspeccion

    # --- Consultas del registro (dict) ---

    def obtener_lote(self, lote_id):
        """Accede al registro de lotes por id (dict access)."""
        return self._registros["lotes"].get(lote_id)

    def obtener_muestra(self, muestra_id):
        """Accede al registro de muestras por id (dict access)."""
        return self._registros["muestras"].get(muestra_id)

    def listar_lotes(self):
        """Retorna todos los lotes registrados."""
        return list(self._registros["lotes"].values())

    def listar_inspecciones(self):
        """Retorna todas las inspecciones registradas."""
        return list(self._registros["inspecciones"].values())