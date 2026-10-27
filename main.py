"""Demo guionada (end-to-end) del sistema de monitoreo de calidad.

Recorre el sistema en el orden de una inspección real y, en cada etapa, provoca
a propósito los errores posibles para mostrar QUÉ se rechaza, POR QUÉ y DÓNDE
se lanza la excepción. Siempre da el mismo resultado (fechas fijas y semillas).

Secciones:
  1. Registro (y errores en los datos de entrada)
  2. Validaciones antes de inspeccionar
  3. Inspecciones del lote 1
  4. Reglas de cierre y decisión de los lotes
  5. Estructuras de datos: recursión, árboles AVL y cola de prioridad (heap)
  6. Serialización (JSON y pickle)
  7. Simulación aleatoria con semilla
  8. Resumen final
"""

import os
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.procedimiento import Procedimiento
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.certificacion import Certificacion
from classes.defecto import DefectoDimensional
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.lista_enlazada import ListaEnlazada
from classes.cola import Cola
from classes.cola_prioridad import ColaPrioridad
from classes.arbol_avl import ArbolAVL
from classes.simulador import Simulador
from classes.excepciones import CalidadError
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra


# ============================================================
#  FUNCIONES AUXILIARES
# ============================================================

def separador(titulo):
    print(f"\n{'=' * 60}")
    print(f"  {titulo}")
    print(f"{'=' * 60}\n")


def subtitulo(texto):
    print(f"\n--- {texto} ---")


def id_corto(objeto):
    return str(objeto.id)[:8]


def texto_historial(historial):
    """Convierte una secuencia de estados en texto: PENDIENTE -> EN_INSPECCION -> ..."""
    return " -> ".join(map(lambda estado: estado.value, historial))


def intentar(descripcion, donde, accion, errores=(CalidadError,), mostrar_detalles=False):
    """Ejecuta una acción que DEBE ser rechazada y muestra el error.

    `accion` es una función sin parámetros (normalmente una lambda): las funciones
    son valores y se pueden pasar como argumento. Como todas las excepciones propias
    heredan de CalidadError, un solo except las captura a todas."""
    print(f"{descripcion}...")
    try:
        accion()
    except errores as e:
        print(f"   [X] RECHAZADO con {type(e).__name__}: {e}")
        print(f"       Se lanza en: {donde}")
        if mostrar_detalles and getattr(e, "detalles", None):
            print(f"       Detalles (**detalles): {e.detalles}")
        return e
    print("   [!] No fue rechazado (no debería pasar)")
    return None


def inspeccionar(empresa, muestra, profesional, equipo, procedimiento, fecha, observaciones):
    """Lanza, ejecuta y cierra una inspección completa."""
    insp = empresa.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)
    insp.ejecutar(observaciones)
    insp.cerrar()
    return insp


def main():
    empresa = Empresa()
    fecha_hoy = date(2025, 6, 15)

    # ============================================================
    #  1. REGISTRO
    # ============================================================
    separador("1. REGISTRO DE LOTES, PROFESIONALES, EQUIPOS Y PROCEDIMIENTOS")

    # Lote 1: 1000 tornillos en 20 muestras de 50. El lote crea sus muestras
    # (composición) y las pone en su cola de pendientes (FIFO).
    lote = empresa.crear_registrar_lote("Tornillos", 1000)
    # *args: [50] * 20 es una lista con veinte 50; el * la desempaqueta en 20 argumentos
    muestras = empresa.crear_registrar_muestras(lote, *[50] * 20)
    capacidad_usada = sum(map(lambda m: m.cantidad, muestras))
    print(f"Lote '{lote.nombre_componentes}' [{id_corto(lote)}]: {len(muestras)} muestras, "
          f"capacidad usada {capacidad_usada}/{lote.cantidad_fabricada}")
    print(f"Muestras pendientes en la cola: {len(lote.pendientes_en_orden())}")
    print(f"¿La muestra 0 pertenece al lote? (muestra in lote, con __contains__): {muestras[0] in lote}")

    # Profesionales
    prof_ana = empresa.crear_registrar_profesional("Ana")
    prof_ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    prof_ana.agregar_certificacion(Certificacion("Seguridad", date(2023, 1, 1), date(2023, 12, 31)))
    prof_bruno = empresa.crear_registrar_profesional("Bruno")
    prof_bruno.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), fecha_hoy))  # vence hoy
    prof_carlos = empresa.crear_registrar_profesional("Carlos")                         # sin certificaciones
    vigentes_ana = ", ".join(map(lambda c: c.nombre, prof_ana.certificaciones_vigentes(fecha_hoy)))
    print(f"Ana: ISO vigente y Seguridad vencida (vigentes hoy: {vigentes_ana})")
    print(f"Bruno: ISO que vence justo hoy ({fecha_hoy})")
    print("Carlos: sin certificaciones")

    # Equipos: la calibración vale 182 días (los extremos se incluyen)
    equipo_visual = empresa.crear_registrar_equipo("Visual", fecha_hoy - timedelta(days=100))
    equipo_borde = empresa.crear_registrar_equipo("Visual", fecha_hoy - timedelta(days=182))
    equipo_dimensional = empresa.crear_registrar_equipo("Dimensional", fecha_hoy - timedelta(days=180))
    equipo_vencido = empresa.crear_registrar_equipo("Visual", fecha_hoy - timedelta(days=183))
    equipo_futuro = empresa.crear_registrar_equipo("Visual", fecha_hoy + timedelta(days=10))
    equipos = {
        "Visual, calibrado hace 100 días": equipo_visual,
        "Visual, calibrado hace 182 días (límite)": equipo_borde,
        "Dimensional, calibrado hace 180 días": equipo_dimensional,
        "Visual, calibrado hace 183 días": equipo_vencido,
        "Visual, calibrado dentro de 10 días": equipo_futuro,
    }
    for nombre, equipo in equipos.items():
        print(f"Equipo {nombre}: ¿calibrado hoy? {equipo.esta_calibrado(fecha_hoy)}")

    # Procedimientos (polimorfismo: misma interfaz, distinto criterio de evaluación)
    proc_visual = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")
    proc_dimensional = empresa.crear_registrar_procedimiento(
        ProcedimientoDimensional, limite_gravedad_acumulada=10, unidad_medida="mm")   # **kwargs
    proc_seguridad = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="Seguridad")
    print("Procedimientos: visual (límite 5, pide ISO), dimensional (límite 10, en mm) "
          "y visual (pide Seguridad)")

    subtitulo("Errores en los datos de entrada")
    intentar("1a. Crear una muestra más (el lote ya usó sus 1000 unidades)",
             "Lote.crear_muestra",
             lambda: empresa.crear_registrar_muestra(1, lote))
    intentar("1b. Crear un lote con cantidad 0",
             "validar_cantidad (validacion.py), desde Lote.__init__",
             lambda: empresa.crear_registrar_lote("Tuercas", 0))
    intentar("1c. Crear una certificación que termina antes de empezar",
             "validar_rango_fechas (validacion.py), desde Certificacion.__init__",
             lambda: Certificacion("ISO", date(2025, 12, 31), date(2025, 1, 1)))
    intentar("1d. Registrar un profesional llamado 'Ana 2' (los nombres de persona son solo letras)",
             "validar_texto (validacion.py), desde Profesional.__init__",
             lambda: empresa.crear_registrar_profesional("Ana 2"))
    print("    En cambio, los nombres técnicos aceptan números: "
          f"{Certificacion('ISO 9001', date(2025, 1, 1), date(2025, 12, 31)).nombre!r} es válido")
    intentar("1e. Crear un Procedimiento genérico (es una clase abstracta)",
             "Python (ABC), porque evaluar() es un @abstractmethod",
             lambda: Procedimiento(limite_gravedad_acumulada=5, categoria_equipo_requerida="Visual"),
             errores=(TypeError,))

    # ============================================================
    #  2. VALIDACIONES ANTES DE INSPECCIONAR
    # ============================================================
    separador("2. VALIDACIONES ANTES DE INSPECCIONAR")

    # El constructor de Inspeccion valida, en este orden: fecha, estado de la muestra,
    # certificación, compatibilidad del equipo y calibración. Si algo falla, lanza la
    # excepción ANTES de tocar la muestra, que sigue PENDIENTE.
    m0 = muestras[0]
    intentar("2a. Inspeccionar con un profesional sin la certificación que pide el procedimiento",
             "Inspeccion.__init__",
             lambda: empresa.lanzar_inspeccion(m0, prof_carlos, equipo_visual, proc_visual, fecha_hoy),
             mostrar_detalles=True)
    intentar("2b. Inspeccionar con una certificación vencida (la de Seguridad de Ana es de 2023)",
             "Inspeccion.__init__ (usa Certificacion.es_vigente)",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_visual, proc_seguridad, fecha_hoy))
    intentar("2c. Inspeccionar con un equipo calibrado hace 183 días (uno más que el máximo)",
             "Inspeccion.__init__ (usa Equipo.esta_calibrado)",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_vencido, proc_visual, fecha_hoy))
    intentar("2d. Inspeccionar con un equipo de otra categoría (dimensional para un procedimiento visual)",
             "Inspeccion.__init__ (usa Equipo.es_compatible)",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_dimensional, proc_visual, fecha_hoy))
    intentar("2e. Inspeccionar con un equipo cuya calibración es POSTERIOR a la inspección",
             "Inspeccion.__init__ (Equipo.esta_calibrado exige calibración <= fecha de inspección)",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_futuro, proc_visual, fecha_hoy))
    intentar("2f. Fallan la certificación Y el equipo a la vez: sale solo el primer error del orden",
             "Inspeccion.__init__",
             lambda: empresa.lanzar_inspeccion(m0, prof_carlos, equipo_vencido, proc_visual, fecha_hoy))
    intentar("2g. Inspeccionar con una fecha escrita como texto en lugar de date",
             "Inspeccion.__init__",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_visual, proc_visual, "2025-06-15"))
    print(f"\nDespués de todos los intentos, la muestra 0 sigue {m0.estado.value} "
          f"y sin inspección asignada: {m0.inspeccion is None}")

    # ============================================================
    #  3. INSPECCIONES DEL LOTE 1
    # ============================================================
    separador("3. INSPECCIONES DEL LOTE 1")

    subtitulo("Muestra 0: inspección visual con un defecto crítico")
    insp_0 = empresa.lanzar_siguiente_inspeccion(          # toma la muestra del front de la cola
        lote, prof_ana, equipo_visual, proc_visual, fecha_hoy)
    defectos_0 = insp_0.ejecutar([
        ObservacionVisual("Fractura completa en pieza", True, 5),
        ObservacionVisual("Decoloración leve", True, 1),
    ])
    insp_0.cerrar()
    for d in defectos_0:
        print(f"  Defecto: {d.descripcion} (gravedad {d.gravedad})")
    print(f"Estado: {m0.estado.value} (tiene un defecto crítico)")
    print(f"Historial de estados (pila, del bottom al top): {texto_historial(m0.historial_estados)}")
    print(f"Se generó el reporte [{id_corto(m0.reporte)}] con copia de {len(m0.reporte.defectos)} defectos")

    subtitulo("Lo que no se puede hacer con una muestra cerrada")
    intentar("3a. Inspeccionar de nuevo la muestra 0",
             "Inspeccion.__init__ (la muestra ya no está PENDIENTE)",
             lambda: empresa.lanzar_inspeccion(m0, prof_ana, equipo_visual, proc_visual, fecha_hoy))
    intentar("3b. Volver a ejecutar la inspección ya cerrada",
             "Inspeccion.ejecutar",
             lambda: insp_0.ejecutar([ObservacionVisual("Raya", True, 1)]))
    intentar("3c. Agregarle un defecto a la muestra cerrada",
             "Muestra.agregar_defecto (solo se puede EN_INSPECCION)",
             lambda: m0.agregar_defecto(defectos_0[0]))
    intentar("3d. Decidir el lote con 19 muestras todavía pendientes",
             "Lote.decidir",
             lambda: lote.decidir())

    subtitulo("Muestras 1 a 18: la cola las entrega en orden de creación")
    for _ in range(18):
        insp = empresa.lanzar_siguiente_inspeccion(        # toma la muestra del front de la cola
            lote, prof_ana, equipo_visual, proc_visual, fecha_hoy)
        insp.ejecutar([ObservacionVisual("Sin defectos observados", False)])
        insp.cerrar()
    print(f"Inspeccionadas y conformes. Pendientes en la cola: {len(lote.pendientes_en_orden())}")

    subtitulo("Muestra 19: inspección dimensional (otro procedimiento, mismo evaluar())")
    # La gravedad depende de cuánto se pasa la medida: exceso = desviación / ancho del rango
    insp_19 = empresa.lanzar_siguiente_inspeccion(
        lote, prof_ana, equipo_dimensional, proc_dimensional, fecha_hoy)
    defectos_19 = insp_19.ejecutar([
        ObservacionDimensional(10.5, 9.0, 10.0, "Pieza fuera de tolerancia superior"),
        ObservacionDimensional(9.5, 9.0, 10.0, "Pieza dentro de tolerancia"),
        ObservacionDimensional(8.0, 9.0, 10.0, "Pieza fuera de tolerancia inferior"),
    ])
    insp_19.cerrar()
    for d in defectos_19:
        print(f"  Defecto: medido {d.valor_medido} en [{d.tolerancia_min}, {d.tolerancia_max}] "
              f"{d.unidad} -> gravedad {d.gravedad}")
    print(f"Suma de gravedades {muestras[19].suma_gravedades()} <= límite 10: {muestras[19].estado.value}")

    intentar("3e. Pedir la siguiente inspección con la cola vacía",
             "Empresa.lanzar_siguiente_inspeccion",
             lambda: empresa.lanzar_siguiente_inspeccion(
                 lote, prof_ana, equipo_visual, proc_visual, fecha_hoy))

    # ============================================================
    #  4. REGLAS DE CIERRE Y DECISIÓN DE LOS LOTES
    # ============================================================
    separador("4. REGLAS DE CIERRE Y DECISIÓN DE LOS LOTES")

    subtitulo("Lote 1: consultas (solo miran muestras cerradas) y decisión")
    print(f"Todas cerradas: {lote.todas_cerradas()} | No conforme: {lote.porcentaje_no_conforme()}% "
          f"| Defectos críticos: {lote.total_defectos_criticos()}")
    for tipo, cantidad in lote.conteo_por_tipo().items():
        print(f"  Defectos {tipo}: {cantidad}")
    no_conformes = list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME, muestras))
    print(f"{len(no_conformes)}/{len(muestras)} no conformes = exactamente 5 %: "
          f"se rechaza solo si SUPERA el 5 % -> {lote.decidir().value}")
    intentar("4a. Decidir el lote otra vez (la decisión es final)",
             "Lote.decidir",
             lambda: lote.decidir())

    subtitulo("Lote 2: un caso por cada regla de cierre (límite de gravedad 5)")
    lote_2 = empresa.crear_registrar_lote("Arandelas", 40)
    intentar("4b. Crear 5 muestras de 10 en un lote de 40 (no entran todas)",
             "Empresa.crear_registrar_muestras (controla el total ANTES de crear)",
             lambda: empresa.crear_registrar_muestras(lote_2, 10, 10, 10, 10, 10))
    print(f"    No se creó ninguna: el lote 2 tiene {len(lote_2.muestras)} muestras")
    # *args: cada cantidad es un argumento; la tupla devuelta se desempaqueta en 4 variables
    m_igual, m_supera, m_critica, m_limpia = empresa.crear_registrar_muestras(lote_2, 10, 10, 10, 10)

    # Bruno (certificación que vence HOY) con el equipo de 182 días: los dos límites se aceptan
    inspeccionar(empresa, m_igual, prof_bruno, equipo_borde, proc_visual, fecha_hoy,
                 [ObservacionVisual("Raya superficial", True, 2),
                  ObservacionVisual("Mancha", True, 3)])
    print(f"Suma igual al límite (2 + 3 = 5): {m_igual.estado.value}  "
          f"<- inspeccionó Bruno, con certificación que vence hoy y equipo de 182 días")
    inspeccionar(empresa, m_supera, prof_ana, equipo_visual, proc_visual, date(2025, 6, 20),
                 [ObservacionVisual("Raya", True, 3), ObservacionVisual("Abolladura", True, 3)])
    print(f"Suma mayor al límite (3 + 3 = 6), sin crítico: {m_supera.estado.value}")
    inspeccionar(empresa, m_critica, prof_ana, equipo_visual, proc_visual, date(2025, 7, 2),
                 [ObservacionVisual("Fisura completa", True, 5)])
    print(f"Un solo defecto crítico (gravedad 5): {m_critica.estado.value}")
    inspeccionar(empresa, m_limpia, prof_ana, equipo_visual, proc_visual, fecha_hoy,
                 [ObservacionVisual("Sin defectos observados", False)])
    print(f"Sin defectos: {m_limpia.estado.value} y sin reporte ({m_limpia.reporte})")
    print(f"2 de 4 no conformes = {lote_2.porcentaje_no_conforme()}% -> {lote_2.decidir().value}")

    subtitulo("Defectos inválidos (regla 3)")
    intentar("4c. Crear una observación con gravedad 6 (tiene que ser de 1 a 5)",
             "validar_rango_entero (validacion.py), desde ObservacionVisual.__init__",
             lambda: ObservacionVisual("Raya profunda", True, 6))
    intentar("4d. Crear un defecto dimensional con la medida DENTRO de la tolerancia",
             "DefectoDimensional.__init__ (un defecto dimensional exige estar fuera de rango)",
             lambda: DefectoDimensional("Pieza", 2, 9.5, 9.0, 10.0))

    # ============================================================
    #  5. ESTRUCTURAS DE DATOS: RECURSIÓN, ÁRBOLES AVL Y HEAP
    # ============================================================
    separador("5. ESTRUCTURAS DE DATOS: RECURSIÓN, ÁRBOLES AVL Y HEAP")

    subtitulo("5.1 Recursión frente a iteración (lista enlazada)")
    lista = ListaEnlazada()
    for valor in [10, 25, 5, 25, 40]:
        lista.insertar_final(valor)
    print(f"Lista: {lista}")
    print(f"  Largo   -> iterativo len(lista) = {len(lista)} | "
          f"recursivo longitud_recursiva() = {lista.longitud_recursiva()}")
    print(f"  Buscar 25 -> iterativo buscar() = {lista.buscar(25)} | "
          f"recursivo buscar_recursivo() = {lista.buscar_recursivo(25)}")
    print(f"  Contar 25 (recursivo): {lista.contar_recursivo(25)}")
    lista.invertir_recursivo()
    print(f"  Invertida recursivamente: {lista}")
    print("  Cada versión recursiva tiene un caso base (nodo None) y un caso recursivo "
          "(el resto de la lista)")

    subtitulo("5.2 Por qué AVL: datos que llegan ordenados")
    arbol = ArbolAVL()
    for clave in range(1, 16):
        arbol.insertar(clave, f"dato {clave}")
    print("Claves 1 a 15 insertadas EN ORDEN (como llegan las fechas de calibración o de reportes):")
    print(f"  Árbol de búsqueda sin balance: quedaría como una cadena de altura 15 (buscar es O(n))")
    print(f"  Árbol AVL: altura {arbol.altura()}, balanceado = {arbol.esta_balanceado()} "
          f"(buscar es O(log n) garantizado)")
    print(f"  Búsqueda recursiva: buscar(11) = {arbol.buscar(11)} | buscar(99) = {arbol.buscar(99)}")

    subtitulo("5.3 Rotaciones (vistas por niveles, con nuestra Cola)")
    rotacion = ArbolAVL()
    for clave in (10, 20, 30):
        rotacion.insertar(clave, clave)
    print(f"Insertar 10, 20, 30 (cargado a la derecha) -> rotación izquierda: {rotacion.niveles()}")
    for clave in (40, 50):
        rotacion.insertar(clave, clave)
    print(f"Agregar 40 y 50 (otra rotación): {rotacion.niveles()}")

    subtitulo("5.4 Equipos ordenados por fecha de calibración (AVL que se mantiene al día)")
    vencidos = empresa.equipos_vencidos_al(fecha_hoy)
    print(f"Equipos vencidos al {fecha_hoy}: "
          f"{list(map(lambda e: f'{e.categoria} calibrado el {e.fecha_calibracion}', vencidos))}")
    a_vencer = empresa.equipos_que_vencen_entre(fecha_hoy, fecha_hoy + timedelta(days=30))
    print(f"Equipos que vencen en los próximos 30 días: "
          f"{list(map(lambda e: f'{e.categoria} vence el {e.fecha_vencimiento}', a_vencer))}")
    primero = empresa.equipo_que_vence_primero(fecha_hoy)
    print(f"El equipo calibrado que vence primero: {primero.categoria} [{id_corto(primero)}], "
          f"vence el {primero.fecha_vencimiento}")

    subtitulo("5.5 Reportes entre dos fechas (búsqueda por rango en el AVL)")
    for desde, hasta, mes in ((date(2025, 6, 1), date(2025, 6, 30), "junio"),
                              (date(2025, 7, 1), date(2025, 7, 31), "julio")):
        reportes_mes = empresa.reportes_entre(desde, hasta)
        print(f"Reportes de {mes}: {list(map(lambda r: str(r.fecha), reportes_mes))}")

    subtitulo("5.6 Otros índices AVL del dominio")
    arbol_defectos = lote_2.arbol_defectos_por_gravedad()
    print(f"Defectos del lote 2 por gravedad: {arbol_defectos} (claves {arbol_defectos.claves_in_orden()})")
    print(f"  Críticos -> buscar(5): {list(map(lambda d: d.descripcion, arbol_defectos.buscar(5)))}")
    print(f"  Graves   -> buscar_rango(3, 5): "
          f"{list(map(lambda d: d.descripcion, arbol_defectos.buscar_rango(3, 5)))}")
    arbol_lotes = empresa.arbol_lotes_por_produccion()
    print(f"Lotes por producción (in-orden): "
          f"{list(map(lambda l: f'{l.nombre_componentes} ({l.cantidad_fabricada})', arbol_lotes))}")

    subtitulo("5.7 Cola de prioridad (max-heap): atender primero los reportes más graves")
    # Como en la sala de urgencias del apunte: no sale el que llegó antes, sale el
    # más grave. Prioridad = (gravedad máxima, suma de gravedades), una tupla.
    cola_atencion = empresa.cola_atencion_reportes()
    print(f"{len(cola_atencion)} reportes en la cola. Orden de atención:")
    for reporte in cola_atencion.en_orden_de_prioridad():
        print(f"  {reporte.fecha} | gravedad máxima {reporte.gravedad_maxima}, "
              f"suma {reporte.suma_gravedades}")
    print(f"Se atiende primero el del {cola_atencion.extraer_maximo().fecha}; "
          f"quedan {len(cola_atencion)}")
    pacientes = ColaPrioridad()
    for paciente, prioridad in (("Esguince", 2), ("Fractura expuesta", 10), ("Fiebre alta", 7)):
        pacientes.insertar(paciente, prioridad)
    print(f"Ejemplo del apunte (llegan Esguince, Fractura expuesta, Fiebre alta): "
          f"se atiende {pacientes.en_orden_de_prioridad()}")
    while pacientes:
        pacientes.extraer_maximo()
    intentar("5a. Atender un paciente con la cola de prioridad vacía",
             "ColaPrioridad.extraer_maximo",
             lambda: pacientes.extraer_maximo())

    subtitulo("5.8 Cola con capacidad máxima (operación full() de la cátedra)")
    cola_chica = Cola(maxsize=2)
    cola_chica.put("A")
    cola_chica.put("B")
    print(f"Cola con maxsize=2 después de 2 put: full() = {cola_chica.full()}")
    intentar("5b. Agregar un tercer elemento",
             "Cola.put",
             lambda: cola_chica.put("C"))

    # ============================================================
    #  6. SERIALIZACIÓN (JSON Y PICKLE)
    # ============================================================
    separador("6. SERIALIZACIÓN (JSON Y PICKLE)")

    subtitulo("JSON: los reportes de desviación, en un archivo legible")
    ruta_json = "reportes.json"
    cantidad = empresa.exportar_reportes_json(ruta_json)          # to_dict() + json.dump
    reportes_cargados = Empresa.cargar_reportes_json(ruta_json)   # json.load + Clase(**data)
    iguales = all(map(lambda par: par[0].to_dict() == par[1].to_dict(),
                      zip(empresa.reportes(), reportes_cargados)))
    print(f"Exportados {cantidad} reportes a '{ruta_json}' y cargados de vuelta. ¿Iguales? {iguales}")

    subtitulo("pickle: la empresa completa, para retomar el trabajo")
    ruta_pkl = "empresa.pkl"
    empresa.guardar(ruta_pkl)                                     # pickle.dump con "wb"
    cargada = Empresa.cargar(ruta_pkl)                            # pickle.load con "rb"
    m0_cargada = cargada.obtener_muestra(m0.id)
    print(f"Guardada en '{ruta_pkl}' y cargada. ¿Es otro objeto? {cargada is not empresa} | "
          f"¿Mismo contenido? {cargada.resumen() == empresa.resumen()}")
    print(f"La muestra 0 recuperada conserva su pila: {texto_historial(m0_cargada.historial_estados)}")
    print(f"Y el índice AVL de equipos: {len(cargada.equipos_vencidos_al(fecha_hoy))} equipo vencido")

    ruta_invalida = "archivo_invalido.pkl"
    try:
        with open(ruta_invalida, "w", encoding="utf-8") as f:
            f.write("esto no es una empresa")
        intentar("6a. Cargar un archivo que no es un pickle de una Empresa",
                 "Empresa.cargar (convierte el error de pickle con raise ... from e)",
                 lambda: Empresa.cargar(ruta_invalida))
    finally:
        # finally se ejecuta SIEMPRE, haya error o no: el archivo temporal nunca queda
        if os.path.exists(ruta_invalida):
            os.remove(ruta_invalida)
            print("    (finally: se borró el archivo temporal)")

    # ============================================================
    #  7. SIMULACIÓN ALEATORIA CON SEMILLA
    # ============================================================
    separador("7. SIMULACIÓN ALEATORIA CON SEMILLA")

    # El Simulador inventa las observaciones al azar; las reglas del dominio no
    # cambian. Con la misma semilla se repite exactamente el mismo caso.
    print("5 observaciones visuales al azar con la semilla 7 (probabilidad de defecto 0.5):")
    for obs in Simulador(7).observaciones_visuales(5, prob_defecto=0.5):
        detalle = f"gravedad {obs.gravedad}" if obs.defecto_detectado else "sin defecto"
        print(f"  - {obs.descripcion}: {detalle}")

    def simular(semilla):
        """Crea un lote de 20 muestras y lo inspecciona entero con observaciones al azar."""
        lote_sim = empresa.crear_registrar_lote("Bulones", 200)
        for _ in range(20):
            empresa.crear_registrar_muestra(10, lote_sim)
        Simulador(semilla).simular_lote(empresa, lote_sim, prof_ana, equipo_visual,
                                        proc_visual, fecha_hoy, prob_defecto=0.15)
        return lote_sim

    print("\nLotes de 20 muestras, probabilidad de defecto 0.15, límite de gravedad 5:")
    lotes_simulados = {}
    for semilla in (5, 1):
        lote_sim = simular(semilla)
        no_conf = len(list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME,
                                  lote_sim.muestras)))
        print(f"  Semilla {semilla}: {no_conf}/20 no conformes ({lote_sim.porcentaje_no_conforme()}%) "
              f"-> {lote_sim.decidir().value}")
        lotes_simulados[semilla] = lote_sim

    estados = lambda lote_x: list(map(lambda m: m.estado, lote_x.muestras))
    print(f"Repitiendo la semilla 5: ¿mismo resultado muestra por muestra? "
          f"{estados(simular(5)) == estados(lotes_simulados[5])}")
    print("Las validaciones se aplican igual que a mano: simular con Carlos daría "
          "CertificacionNoVigenteError (caso 2a)")

    # ============================================================
    #  8. RESUMEN FINAL
    # ============================================================
    separador("8. RESUMEN FINAL")

    print(f"Lote 1 '{lote.nombre_componentes}': {lote.estado.value} | "
          f"Lote 2 '{lote_2.nombre_componentes}': {lote_2.estado.value}")

    print("\nReportes de desviación (uno por cada muestra no conforme), con sus defectos")
    print("del más grave al menos grave (sorted, que compara con Defecto.__lt__):")
    for r in empresa.reportes()[:3]:
        print(f"  [{id_corto(r)}] {r.fecha} | muestra [{str(r.muestra_id)[:8]}] | "
              f"gravedad máxima {r.gravedad_maxima} (calculada con reduce) | "
              f"{texto_historial(r.historial_estados)}")
        for d in r.defectos_por_gravedad():
            print(f"      - {d.descripcion} (gravedad {d.gravedad})")
    print(f"  ... y {len(empresa.reportes()) - 3} más de los lotes simulados")

    print("\nConsultas con filtros **kwargs:")
    print(f"  Lotes APROBADOS: {len(empresa.listar_lotes(estado=EstadoLote.APROBADO))} | "
          f"RECHAZADOS: {len(empresa.listar_lotes(estado=EstadoLote.RECHAZADO))}")
    print(f"  Muestras NO_CONFORME: {len(empresa.listar_muestras(estado=EstadoMuestra.NO_CONFORME))} | "
          f"Inspecciones cerradas: {len(empresa.listar_inspecciones(cerrada=True))}")
    print(f"  Equipos visuales: {len(empresa.listar_equipos(categoria='Visual'))}")
    intentar("8a. Filtrar por un atributo que no existe ('estdo')",
             "Empresa._filtrar",
             lambda: empresa.listar_lotes(estdo=EstadoLote.APROBADO))

    print("\nRegistro de la empresa:")
    for categoria, cantidad in empresa.resumen().items():
        print(f"  - {categoria}: {cantidad}")

    print(f"\n{'=' * 60}")
    print("  [OK] EJECUCION COMPLETA - TODAS LAS FUNCIONALIDADES DEMOSTRADAS")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
