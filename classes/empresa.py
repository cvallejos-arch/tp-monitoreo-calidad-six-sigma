import json
import pickle
from datetime import date, timedelta

from classes.lote import Lote
from classes.muestra import Muestra
from classes.inspeccion import Inspeccion
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.procedimiento import Procedimiento
from classes.reporte import Reporte
from classes.arbol_avl import ArbolAVL
from classes.cola_prioridad import ColaPrioridad
from classes.excepciones import EstructuraVaciaError, DatosInvalidosError, TransicionIlegalError
from classes.validacion import validar_fecha_tipo, validar_rango_fechas, validar_cantidad

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
        # Índice de equipos ordenado por fecha de calibración. Se mantiene al día:
        # cada equipo se inserta al registrarlo (O(log n)), así las consultas por
        # fecha no tienen que recorrer ni reordenar todos los equipos.
        self._equipos_por_calibracion = ArbolAVL()

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

    def crear_registrar_muestras(self, lote, *cantidades):
        """Crea varias muestras en el lote, una por cada cantidad recibida.
        Ejemplo: crear_registrar_muestras(lote, 50, 50, 30) crea 3 muestras.

        *cantidades junta los argumentos posicionales en una TUPLA, así que acepta
        cualquier cantidad de muestras (también se puede desempaquetar una lista:
        crear_registrar_muestras(lote, *[10] * 20)).

        Todo se valida ANTES de crear: si alguna cantidad es inválida o entre todas
        superan la capacidad libre del lote, no se crea ninguna.
        Retorna una tupla con las muestras creadas."""
        if not cantidades:
            raise DatosInvalidosError("Hay que indicar al menos una cantidad de unidades")
        for cantidad in cantidades:
            validar_cantidad(cantidad)
        total = sum(cantidades)
        if total > lote.capacidad_libre:
            raise TransicionIlegalError(
                f"Las {len(cantidades)} muestras suman {total} unidades y al lote le quedan "
                f"{lote.capacidad_libre}: no se crea ninguna.",
                lote_id=lote.id,
                cantidad_solicitada=total,
                capacidad_libre=lote.capacidad_libre
            )
        return tuple(map(lambda cantidad: self.crear_registrar_muestra(cantidad, lote), cantidades))

    def crear_registrar_profesional(self, nombre):
        """Crea y registra un profesional en el sistema."""
        profesional = Profesional(nombre)
        self._registros["profesionales"][profesional.id] = profesional
        return profesional

    def crear_registrar_equipo(self, categoria, fecha_calibracion):
        """Crea y registra un equipo en el sistema."""
        equipo = Equipo(categoria, fecha_calibracion)
        self._registros["equipos"][equipo.id] = equipo
        self._equipos_por_calibracion.insertar(equipo.fecha_calibracion, equipo)
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

    def _filtrar(self, nombre_registro, **filtros):
        """Retorna los objetos de una categoría del registro que cumplen TODOS los
        filtros {atributo: valor}. Sin filtros, retorna todos.
        Lanza DatosInvalidosError si algún atributo no existe en esa clase.
        El parámetro se llama nombre_registro (y no 'categoria') para no chocar con
        un filtro por atributo: Equipo tiene un atributo 'categoria'."""
        clase = Empresa.CLASES_POR_CATEGORIA[nombre_registro]

        # Se recorren los filtros (dict) para validar que cada atributo exista.
        for attr in filtros.keys():
            if not hasattr(clase, attr):
                raise DatosInvalidosError(
                    f"'{clase.__name__}' no tiene el atributo '{attr}' para filtrar.",
                    registro=nombre_registro,
                    atributo=attr
                )

        # Un objeto pasa el filtro si coincide en todos los pares (atributo, valor).
        return list(
            filter(
                lambda obj: all(
                    map(lambda par: getattr(obj, par[0]) == par[1], filtros.items())
                ),
                self._registros[nombre_registro].values()
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

    def listar_profesionales(self, **filtros):
        """Retorna los profesionales registrados, opcionalmente filtrados por atributos (kwargs)."""
        return self._filtrar("profesionales", **filtros)

    def listar_equipos(self, **filtros):
        """Retorna los equipos registrados, opcionalmente filtrados por atributos (kwargs)."""
        return self._filtrar("equipos", **filtros)

    def listar_procedimientos(self, **filtros):
        """Retorna los procedimientos registrados, opcionalmente filtrados por atributos (kwargs)."""
        return self._filtrar("procedimientos", **filtros)

    def resumen(self):
        """Retorna un dict {categoria: cantidad registrada}, recorriendo el registro."""
        return dict(
            map(
                lambda par: (par[0], len(par[1])),
                self._registros.items()
            )
        )

    # --- Conjuntos: quiénes y con qué se inspeccionó cada lote ---

    def _inspecciones_de_lote(self, lote):
        """Inspecciones de las muestras del lote. Los ids de sus muestras se guardan
        en un set: preguntar `id in conjunto` usa el hash y no recorre nada (O(1))."""
        ids_muestras = set(map(lambda m: m.id, lote.muestras))
        return filter(lambda i: i.muestra_id in ids_muestras,
                      self._registros["inspecciones"].values())

    def profesionales_de_lote(self, lote):
        """Conjunto de profesionales que inspeccionaron el lote, sin repetir.
        Guardar Profesional en un set es posible gracias a __eq__ y __hash__ (Entidad)."""
        profesionales = self._registros["profesionales"]
        return set(map(lambda i: profesionales[i.profesional_id], self._inspecciones_de_lote(lote)))

    def equipos_de_lote(self, lote):
        """Conjunto de equipos usados en el lote (por ejemplo, para revisarlos si se rechazó)."""
        equipos = self._registros["equipos"]
        return set(map(lambda i: equipos[i.equipo_id], self._inspecciones_de_lote(lote)))

    def profesionales_en_comun(self, lote_a, lote_b):
        """Profesionales que inspeccionaron los DOS lotes (intersección, &)."""
        return self.profesionales_de_lote(lote_a) & self.profesionales_de_lote(lote_b)

    def profesionales_solo_en(self, lote_a, lote_b):
        """Profesionales que inspeccionaron lote_a pero NO lote_b (diferencia, -)."""
        return self.profesionales_de_lote(lote_a) - self.profesionales_de_lote(lote_b)

    # --- Índices con árbol AVL ---

    def arbol_lotes_por_produccion(self):
        """Retorna un ArbolAVL con los lotes registrados, indexados por cantidad
        fabricada: permite listarlos ordenados y buscar por volumen de producción."""
        arbol = ArbolAVL()
        for lote in self._registros["lotes"].values():
            arbol.insertar(lote.cantidad_fabricada, lote)
        return arbol

    # Equipos por fecha de calibración (el árbol se mantiene actualizado).
    # Un equipo vale hasta fecha_calibracion + 182 días: preguntar por fechas de
    # vencimiento equivale a preguntar por un rango de fechas de calibración.

    def equipos_por_calibracion(self):
        """Todos los equipos, del calibrado hace más tiempo al más reciente."""
        return self._equipos_por_calibracion.recorrido_in_orden()

    def equipos_vencidos_al(self, fecha):
        """Equipos con la calibración vencida en esa fecha: los calibrados hace más
        de 182 días. Es una búsqueda por rango en el árbol: calibración <= fecha - 183 días."""
        validar_fecha_tipo(fecha, "fecha")
        limite = fecha - timedelta(days=Equipo.DIAS_VALIDEZ_CALIBRACION + 1)
        return self._equipos_por_calibracion.buscar_rango(date.min, limite)

    def equipos_que_vencen_entre(self, desde, hasta):
        """Equipos cuya calibración vence entre desde y hasta (ambos incluidos),
        ordenados del que vence primero al último. Sirve para avisar con tiempo,
        por ejemplo los que vencen en los próximos 30 días."""
        validar_rango_fechas(desde, hasta)
        dias = timedelta(days=Equipo.DIAS_VALIDEZ_CALIBRACION)
        return self._equipos_por_calibracion.buscar_rango(desde - dias, hasta - dias)

    def equipo_que_vence_primero(self, fecha):
        """Entre los equipos calibrados en esa fecha, el que vence antes
        (None si no hay ninguno calibrado)."""
        validar_fecha_tipo(fecha, "fecha")
        dias = timedelta(days=Equipo.DIAS_VALIDEZ_CALIBRACION)
        calibrados = self._equipos_por_calibracion.buscar_rango(fecha - dias, fecha)
        return calibrados[0] if calibrados else None

    # Reportes por fecha (el árbol se arma en cada consulta: los reportes los crea
    # la Muestra al cerrarse, no la Empresa, así que no hay un momento único donde
    # insertarlos sin cambiar el flujo de las inspecciones).

    def arbol_reportes_por_fecha(self):
        """Retorna un ArbolAVL con los reportes de desviación, indexados por fecha."""
        arbol = ArbolAVL()
        for reporte in self.reportes():
            arbol.insertar(reporte.fecha, reporte)
        return arbol

    def reportes_entre(self, desde, hasta):
        """Reportes de desviación con fecha entre desde y hasta (ambos incluidos),
        ordenados por fecha. Por ejemplo, todos los rechazos de un mes."""
        validar_rango_fechas(desde, hasta)
        return self.arbol_reportes_por_fecha().buscar_rango(desde, hasta)

    # --- Cola de prioridad (heap) ---

    def cola_atencion_reportes(self, desde=None, hasta=None):
        """Retorna una ColaPrioridad (max-heap) con los reportes de desviación, para
        atenderlos del más grave al menos grave, como en una sala de urgencias.
        Si se indican desde y hasta, solo entran los reportes de ese período.

        Prioridad = (gravedad máxima, suma de gravedades): las tuplas se comparan
        elemento a elemento, así que primero decide el defecto más grave (un crítico
        va antes que todo) y, si empatan, la suma. Si también empatan, sale primero
        el que llegó antes: por eso se insertan en orden de fecha (recorrido
        in-orden del AVL de reportes)."""
        if desde is None and hasta is None:
            reportes = self.arbol_reportes_por_fecha().recorrido_in_orden()
        else:
            reportes = self.reportes_entre(desde, hasta)    # también vienen en orden de fecha
        cola = ColaPrioridad()
        for reporte in reportes:
            cola.insertar(reporte, (reporte.gravedad_maxima, reporte.suma_gravedades))
        return cola

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