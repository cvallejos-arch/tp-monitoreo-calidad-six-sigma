from classes.lote import Lote
from classes.procedimiento import Procedimiento
from classes.inspeccion import Inspeccion
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.muestra import Muestra
from classes.excepciones import EstructuraVaciaError

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

    def crear_registrar_muestra(self, cantidad, lote):
        """Crea una muestra dentro de un lote y la registra (composicion)."""
        muestra = lote.crear_muestra(cantidad)
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
    
    def lanzar_siguiente_inspeccion(self, lote, profesional, equipo, procedimiento, fecha):
        """Lanza la inspección de la próxima muestra pendiente del lote."""
        muestra = lote.siguiente_muestra_pendiente()
        if muestra is None:
            raise EstructuraVaciaError(
                f"El lote '{lote.id}' no tiene muestras pendientes.", lote_id=lote.id
            )
        return self.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)

    # --- Consultas del registro (dict) ---

    def obtener_lote(self, lote_id):
        """Accede al registro de lotes por id (dict access)."""
        return self._registros["lotes"].get(lote_id)

    def obtener_muestra(self, muestra_id):
        """Accede al registro de muestras por id (dict access)."""
        return self._registros["muestras"].get(muestra_id)

    def listar_lotes(self, **filtros):
        """Retorna los lotes registrados, opcionalmente filtrados por atributos (kwargs)."""
        lotes = self._registros["lotes"].values()
        for attr, val in filtros.items():
            lotes = [l for l in lotes if getattr(l, attr, None) == val]
        return list(lotes)

    def listar_inspecciones(self, **filtros):
        """Retorna las inspecciones registradas, opcionalmente filtradas por atributos (kwargs)."""
        inspecciones = self._registros["inspecciones"].values()
        for attr, val in filtros.items():
            inspecciones = [i for i in inspecciones if getattr(i, attr, None) == val]
        return list(inspecciones)

    def listar_muestras(self, **filtros):
        """Retorna las muestras registradas, opcionalmente filtradas por atributos (kwargs)."""
        muestras = self._registros["muestras"].values()
        for attr, val in filtros.items():
            muestras = [m for m in muestras if getattr(m, attr, None) == val]
        return list(muestras)