import json
import pickle

from classes.lote import Lote
from classes.muestra import Muestra
from classes.inspeccion import Inspeccion
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.procedimiento import Procedimiento
from classes.reporte import Reporte
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError

class Empresa:
    # Clase de los objetos guardados en cada categoría del registro
    # (se usa para validar los atributos de los filtros).
    CLASES_POR_CATEGORIA = {
        "lotes": Lote,
        "muestras": Muestra,
        "profesionales": Profesional,
        "equipos": Equipo,
        "procedimientos": Procedimiento,
        "inspecciones": Inspeccion,
    }

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

    def _filtrar(self, categoria, **filtros):
        """Retorna los objetos de una categoría del registro que cumplen TODOS los
        filtros {atributo: valor}. Sin filtros, retorna todos.
        Lanza DatosInvalidosError si algún atributo no existe en esa clase."""
        clase = Empresa.CLASES_POR_CATEGORIA[categoria]

        # Se recorren los filtros (dict) para validar que cada atributo exista.
        for attr in filtros.keys():
            if not hasattr(clase, attr):
                raise DatosInvalidosError(
                    f"'{clase.__name__}' no tiene el atributo '{attr}' para filtrar.",
                    categoria=categoria,
                    atributo=attr
                )

        # Un objeto pasa el filtro si coincide en todos los pares (atributo, valor).
        return list(
            filter(
                lambda obj: all(
                    map(lambda par: getattr(obj, par[0]) == par[1], filtros.items())
                ),
                self._registros[categoria].values()
            )
        )

    def listar_lotes(self, **filtros):
        """Retorna los lotes registrados, opcionalmente filtrados por atributos (kwargs)."""
        return self._filtrar("lotes", **filtros)

    def listar_muestras(self, **filtros):
        """Retorna las muestras registradas, opcionalmente filtradas por atributos (kwargs)."""
        return self._filtrar("muestras", **filtros)

    def listar_inspecciones(self, **filtros):
        """Retorna las inspecciones registradas, opcionalmente filtradas por atributos (kwargs)."""
        return self._filtrar("inspecciones", **filtros)

    def resumen(self):
        """Retorna un dict {categoria: cantidad registrada}, recorriendo el registro."""
        return dict(
            map(
                lambda par: (par[0], len(par[1])),
                self._registros.items()
            )
        )

    # --- Serialización JSON de reportes ---

    def reportes(self):
        """Retorna los reportes de desviación de todas las muestras no conformes."""
        con_reporte = filter(
            lambda m: m.reporte is not None,
            self._registros["muestras"].values()
        )
        return list(map(lambda m: m.reporte, con_reporte))

    def exportar_reportes_json(self, ruta):
        """Guarda los reportes en un archivo JSON legible (serialización).
        Retorna la cantidad de reportes guardados."""
        datos = list(map(lambda r: r.to_dict(), self.reportes()))
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        return len(datos)

    @staticmethod
    def cargar_reportes_json(ruta):
        """Lee un archivo generado por exportar_reportes_json y reconstruye los
        reportes (deserialización). Lanza DatosInvalidosError si el contenido no
        es un JSON de reportes válido."""
        with open(ruta, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError as e:
                raise DatosInvalidosError(
                    f"El archivo '{ruta}' no contiene un JSON válido.", ruta=str(ruta)
                ) from e

        if not isinstance(datos, list):
            raise DatosInvalidosError(
                f"El archivo '{ruta}' debe contener una lista de reportes.", ruta=str(ruta)
            )
        try:
            return list(map(Reporte.from_dict, datos))
        except (KeyError, TypeError, ValueError) as e:
            raise DatosInvalidosError(
                f"El archivo '{ruta}' tiene reportes con datos incompletos o inválidos.",
                ruta=str(ruta)
            ) from e

    # --- Serialización pickle de toda la empresa ---

    def guardar(self, ruta):
        """Guarda la empresa completa en un archivo binario (serialización con pickle):
        lotes, muestras (con su pila de estados), colas de pendientes, profesionales,
        equipos, procedimientos, inspecciones y reportes, con sus relaciones."""
        with open(ruta, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def cargar(cls, ruta):
        """Reconstruye una empresa guardada con guardar() (deserialización).
        Lanza DatosInvalidosError si el archivo no es un pickle válido o si no
        contiene una Empresa. Solo cargar archivos propios: pickle puede ejecutar
        código al leer un archivo de origen desconocido."""
        with open(ruta, "rb") as f:
            try:
                empresa = pickle.load(f)
            except (pickle.UnpicklingError, EOFError) as e:
                raise DatosInvalidosError(
                    f"El archivo '{ruta}' no es un pickle válido.", ruta=str(ruta)
                ) from e

        if not isinstance(empresa, cls):
            raise DatosInvalidosError(
                f"El archivo '{ruta}' no contiene una {cls.__name__}, "
                f"sino un '{type(empresa).__name__}'.",
                ruta=str(ruta)
            )
        return empresa
