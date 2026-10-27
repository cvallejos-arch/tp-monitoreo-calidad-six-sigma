"""Menú por consola del sistema de monitoreo de calidad (QuantumTech Precision).
Es la alternativa a la interfaz gráfica (interfaz.py) cuando la computadora no puede
abrir ventanas. Toda la lógica está en las clases de classes/: este archivo solo
pide datos con input(), llama a esas clases y muestra los resultados.

Ningún error corta el programa: las excepciones del sistema (CalidadError) se
capturan en el bucle principal, se muestran y se vuelve al menú.
Se corre con: py consola.py"""

from datetime import date, timedelta

from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.simulador import Simulador
from classes.excepciones import CalidadError, DatosInvalidosError


# ============================================================
#  ENTRADA DE DATOS (vuelven a preguntar hasta que el dato sea válido)
# ============================================================

def pedir_texto(mensaje, obligatorio=True):
    """Pide un texto. Si es obligatorio, vuelve a preguntar mientras esté vacío."""
    while True:
        texto = input(f"{mensaje}: ").strip()
        if texto or not obligatorio:
            return texto
        print("  [!] El dato no puede estar vacío")


def pedir_entero(mensaje, minimo=None, maximo=None):
    """Pide un entero, opcionalmente dentro de [minimo, maximo]."""
    while True:
        texto = pedir_texto(mensaje)
        try:
            valor = int(texto)
        except ValueError:
            print(f"  [!] '{texto}' no es un número entero")
            continue
        if minimo is not None and valor < minimo:
            print(f"  [!] Tiene que ser mayor o igual a {minimo}")
        elif maximo is not None and valor > maximo:
            print(f"  [!] Tiene que ser menor o igual a {maximo}")
        else:
            return valor


def pedir_decimal(mensaje, minimo=None, maximo=None):
    """Pide un número decimal (acepta coma o punto), opcionalmente en [minimo, maximo]."""
    while True:
        texto = pedir_texto(mensaje).replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            print(f"  [!] '{texto}' no es un número")
            continue
        if minimo is not None and valor < minimo:
            print(f"  [!] Tiene que ser mayor o igual a {minimo}")
        elif maximo is not None and valor > maximo:
            print(f"  [!] Tiene que ser menor o igual a {maximo}")
        else:
            return valor


def pedir_fecha(mensaje):
    """Pide una fecha AAAA-MM-DD. Enter vacío = fecha de hoy."""
    while True:
        texto = pedir_texto(f"{mensaje} (AAAA-MM-DD, Enter = hoy)", obligatorio=False)
        if texto == "":
            return date.today()
        try:
            return date.fromisoformat(texto)
        except ValueError:
            print(f"  [!] '{texto}' no es una fecha válida (formato AAAA-MM-DD)")


def pedir_si_no(mensaje):
    """Pide una respuesta s/n. Vuelve a preguntar ante cualquier otra respuesta."""
    while True:
        respuesta = pedir_texto(f"{mensaje} (s/n)").lower()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("  [!] Respondé 's' o 'n'")


def elegir_de_lista(titulo, opciones, describir):
    """Muestra una lista numerada y devuelve el objeto elegido.
    Lanza DatosInvalidosError si no hay nada para elegir."""
    if not opciones:
        raise DatosInvalidosError(f"No hay {titulo} cargados todavía")
    print(f"\n{titulo.capitalize()}:")
    for numero, obj in enumerate(opciones, start=1):
        print(f"  {numero}. {describir(obj)}")
    numero = pedir_entero("Elegí un número", minimo=1, maximo=len(opciones))
    return opciones[numero - 1]


def pedir_hasta_que_sea_valido(crear):
    """Ejecuta `crear()` hasta que no lance una excepción del sistema.
    Sirve para objetos cuyas reglas valida el dominio (por ejemplo, una
    ObservacionDimensional con tolerancias invertidas)."""
    while True:
        try:
            return crear()
        except CalidadError as e:
            print(f"  [!] {type(e).__name__}: {e}")


# ============================================================
#  DESCRIPCIONES CORTAS (para no mostrar los UUID completos)
# ============================================================

def id_corto(obj):
    return str(obj.id)[:8]


def texto_historial(historial):
    return " -> ".join(map(lambda estado: estado.value, historial))


def describir_lote(lote):
    return (f"{lote.nombre_componentes} [{id_corto(lote)}] - {lote.estado.value} - "
            f"{len(lote.muestras)} muestras ({len(lote.pendientes_en_orden())} pendientes)")


def describir_muestra(muestra):
    return f"Muestra [{id_corto(muestra)}] - {muestra.cantidad} unidades - {muestra.estado.value}"


def describir_profesional(prof):
    certs = ", ".join(map(lambda c: f"{c.nombre} ({c.fecha_inicio} a {c.fecha_fin})",
                          prof.certificaciones.values()))
    return f"{prof.nombre} [{id_corto(prof)}] - certificaciones: {certs or 'ninguna'}"


def describir_equipo(equipo):
    vencido = "" if equipo.esta_calibrado(date.today()) else " - VENCIDO hoy"
    return f"{equipo.categoria} [{id_corto(equipo)}] - calibrado el {equipo.fecha_calibracion}{vencido}"


def describir_procedimiento(proc):
    tipo = "Visual" if isinstance(proc, ProcedimientoVisual) else "Dimensional"
    return (f"{tipo} [{id_corto(proc)}] - límite {proc.limite_gravedad_acumulada} - "
            f"certificación: {proc.certificacion_requerida or 'ninguna'}")


# ============================================================
#  ACCIONES DEL MENÚ (cada una recibe la empresa)
# ============================================================

def crear_lote(empresa):
    nombre = pedir_texto("Nombre de los componentes (ej: Tornillos M8)")
    cantidad = pedir_entero("Cantidad fabricada", minimo=1)
    lote = empresa.crear_registrar_lote(nombre, cantidad)
    print(f"[OK] Lote creado: {describir_lote(lote)}")


def crear_muestras(empresa):
    lote = elegir_de_lista("lotes", empresa.listar_lotes(), describir_lote)
    print(f"Capacidad libre del lote: {lote.capacidad_libre} unidades")
    cantidad = pedir_entero("¿Cuántas muestras?", minimo=1)
    unidades = pedir_entero("Unidades por muestra", minimo=1)
    # crear_registrar_muestras controla el total ANTES de crear (si no entran
    # todas, no crea ninguna). [unidades] * cantidad se desempaqueta con *.
    empresa.crear_registrar_muestras(lote, *[unidades] * cantidad)
    print(f"[OK] Se crearon {cantidad} muestras. {describir_lote(lote)}")


def registrar_profesional(empresa):
    nombre = pedir_texto("Nombre del profesional (solo letras)")
    prof = empresa.crear_registrar_profesional(nombre)
    print(f"[OK] Profesional registrado: {describir_profesional(prof)}")


def agregar_certificacion(empresa):
    prof = elegir_de_lista("profesionales", empresa.listar_profesionales(), describir_profesional)
    nombre = pedir_texto("Nombre de la certificación (ej: ISO 9001)")
    inicio = pedir_fecha("Fecha de inicio")
    fin = pedir_fecha("Fecha de fin")
    prof.agregar_certificacion(Certificacion(nombre, inicio, fin))
    print(f"[OK] {describir_profesional(prof)}")


def registrar_equipo(empresa):
    print("Categorías: 1. Visual  2. Dimensional")
    categoria = ("Visual", "Dimensional")[pedir_entero("Elegí la categoría", 1, 2) - 1]
    fecha = pedir_fecha("Fecha de calibración")
    equipo = empresa.crear_registrar_equipo(categoria, fecha)
    print(f"[OK] Equipo registrado: {describir_equipo(equipo)} (la calibración vale 182 días)")


def crear_procedimiento(empresa):
    print("Tipos: 1. Visual  2. Dimensional")
    tipo = (ProcedimientoVisual, ProcedimientoDimensional)[pedir_entero("Elegí el tipo", 1, 2) - 1]
    datos = {"limite_gravedad_acumulada": pedir_entero("Límite de gravedad acumulada", minimo=1)}
    certificacion = pedir_texto("Certificación requerida (Enter = ninguna)", obligatorio=False)
    if certificacion:
        datos["certificacion_requerida"] = certificacion
    proc = empresa.crear_registrar_procedimiento(tipo, **datos)  # **kwargs
    print(f"[OK] Procedimiento creado: {describir_procedimiento(proc)}")


def pedir_observaciones(procedimiento):
    """Pide las observaciones según el tipo de procedimiento: a mano o al azar."""
    if pedir_si_no("¿Generar las observaciones al azar?"):
        semilla = pedir_texto("Semilla (Enter = al azar)", obligatorio=False)
        cantidad = pedir_entero("¿Cuántas observaciones?", minimo=1)
        simulador = Simulador(int(semilla) if semilla.lstrip("-").isdigit() else None)
        observaciones = simulador.observaciones_para(procedimiento, cantidad)
        for obs in observaciones:
            print(f"  - {obs}")
        return observaciones

    cantidad = pedir_entero("¿Cuántas observaciones vas a registrar?", minimo=1)
    observaciones = []
    for numero in range(1, cantidad + 1):
        print(f"\n  Observación {numero}:")
        descripcion = pedir_texto("  Descripción")
        if isinstance(procedimiento, ProcedimientoVisual):
            if pedir_si_no("  ¿Se detectó un defecto?"):
                gravedad = pedir_entero("  Gravedad (1 a 5)", minimo=1, maximo=5)
                observaciones.append(ObservacionVisual(descripcion, True, gravedad))
            else:
                observaciones.append(ObservacionVisual(descripcion, False))
        else:
            observaciones.append(pedir_hasta_que_sea_valido(lambda: ObservacionDimensional(
                pedir_decimal("  Valor medido"),
                pedir_decimal("  Tolerancia mínima"),
                pedir_decimal("  Tolerancia máxima"),
                descripcion
            )))
    return observaciones


def inspeccionar(empresa):
    lote = elegir_de_lista("lotes", empresa.listar_lotes(), describir_lote)
    if pedir_si_no("¿Tomar la siguiente muestra de la cola?"):
        muestra = lote.siguiente_muestra_pendiente()  # front de la cola
        if muestra is None:
            raise DatosInvalidosError("Este lote no tiene muestras pendientes")
        print(f"Muestra tomada de la cola: {describir_muestra(muestra)}")
    else:
        muestra = elegir_de_lista("muestras", list(lote.muestras), describir_muestra)

    prof = elegir_de_lista("profesionales", empresa.listar_profesionales(), describir_profesional)
    equipo = elegir_de_lista("equipos", empresa.listar_equipos(), describir_equipo)
    proc = elegir_de_lista("procedimientos", empresa.listar_procedimientos(), describir_procedimiento)
    fecha = pedir_fecha("Fecha de la inspección")

    # Las observaciones se piden ANTES de iniciar la inspección: si el usuario
    # se equivoca o cancela, la muestra no queda a medias en EN_INSPECCION.
    observaciones = pedir_observaciones(proc)

    # Inspeccion valida en su constructor (estado, certificación, equipo) antes de
    # cambiar la muestra; si algo falla, lanza la excepción y la muestra no cambia.
    insp = empresa.lanzar_inspeccion(muestra, prof, equipo, proc, fecha)
    defectos = insp.ejecutar(observaciones)
    insp.cerrar()

    print(f"\nDefectos generados: {len(defectos)}")
    for d in defectos:
        print(f"  - {d}")
    print(f"[OK] Muestra cerrada como {muestra.estado.value} | suma de gravedades "
          f"{muestra.suma_gravedades()} (límite {proc.limite_gravedad_acumulada}) | "
          f"¿defecto crítico? {muestra.tiene_critico()}")
    if muestra.reporte is not None:
        print(f"     Se generó un reporte de desviación [{id_corto(muestra.reporte)}]")


def ver_lote(empresa):
    lote = elegir_de_lista("lotes", empresa.listar_lotes(), describir_lote)
    usada = sum(map(lambda m: m.cantidad, lote.muestras))
    print(f"\n{describir_lote(lote)}")
    print(f"Capacidad usada: {usada}/{lote.cantidad_fabricada}")
    for m in lote.muestras:
        print(f"  - {describir_muestra(m)} | historial (pila): {texto_historial(m.historial_estados)}")
    print(f"Todas cerradas: {lote.todas_cerradas()}")
    print(f"Porcentaje no conforme: {lote.porcentaje_no_conforme()}%")
    print(f"Defectos críticos: {lote.total_defectos_criticos()}")
    for tipo, cantidad in lote.conteo_por_tipo().items():
        print(f"  - {tipo}: {cantidad}")


def decidir_lote(empresa):
    lote = elegir_de_lista("lotes", empresa.listar_lotes(), describir_lote)
    estado = lote.decidir()
    print(f"[OK] Lote {estado.value} ({lote.porcentaje_no_conforme()}% no conforme; "
          f"se rechaza si supera el 5%)")


def ver_reportes(empresa):
    reportes = empresa.reportes()
    if not reportes:
        print("No hay reportes: todavía no hay muestras no conformes")
        return
    for r in reportes:
        print(f"\nReporte [{id_corto(r)}] - muestra [{str(r.muestra_id)[:8]}] - fecha {r.fecha}")
        print(f"  Historial: {texto_historial(r.historial_estados)}")
        for d in r.defectos:
            print(f"  - {d}")


def archivos(empresa):
    """Guardar o cargar con pickle, y exportar o importar reportes con JSON.
    Retorna la empresa que queda en uso (cambia al cargar un pickle)."""
    print("1. Guardar empresa (pickle)   2. Cargar empresa (pickle)")
    print("3. Exportar reportes (JSON)   4. Ver reportes de un JSON")
    opcion = pedir_entero("Elegí una opción", 1, 4)
    if opcion == 1:
        ruta = pedir_texto("Archivo (ej: empresa.pkl)")
        empresa.guardar(ruta)
        print(f"[OK] Empresa guardada en '{ruta}'")
    elif opcion == 2:
        ruta = pedir_texto("Archivo (ej: empresa.pkl)")
        empresa = Empresa.cargar(ruta)
        print(f"[OK] Empresa cargada: {empresa.resumen()}")
    elif opcion == 3:
        ruta = pedir_texto("Archivo (ej: reportes.json)")
        print(f"[OK] Se exportaron {empresa.exportar_reportes_json(ruta)} reporte(s) a '{ruta}'")
    else:
        ruta = pedir_texto("Archivo (ej: reportes.json)")
        for r in Empresa.cargar_reportes_json(ruta):
            print(f"  - {r}")
    return empresa


def cargar_datos_ejemplo(empresa):
    """Deja todo listo para probar sin tipear: incluye casos que generan errores."""
    hoy = date.today()
    lote = empresa.crear_registrar_lote("Tornillos M8", 200)
    for _ in range(20):
        empresa.crear_registrar_muestra(10, lote)
    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", hoy - timedelta(days=30), hoy + timedelta(days=335)))
    empresa.crear_registrar_profesional("Carlos")                     # sin certificaciones
    empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=30))
    empresa.crear_registrar_equipo("Dimensional", hoy - timedelta(days=60))
    empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=200))  # vencido
    empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5,
                                          certificacion_requerida="ISO")
    empresa.crear_registrar_procedimiento(ProcedimientoDimensional, limite_gravedad_acumulada=10)
    print("[OK] Datos de ejemplo cargados:")
    print("     - Lote de 200 tornillos con 20 muestras de 10")
    print("     - Ana (ISO vigente) y Carlos (sin certificaciones)")
    print("     - Equipo visual, equipo dimensional y un equipo visual VENCIDO (200 días)")
    print("     - Procedimiento visual (límite 5, pide ISO) y dimensional (límite 10)")


def simulacion_aleatoria(empresa):
    """Inspecciona todas las muestras pendientes de un lote con observaciones al azar."""
    lote = elegir_de_lista("lotes", empresa.listar_lotes(), describir_lote)
    prof = elegir_de_lista("profesionales", empresa.listar_profesionales(), describir_profesional)
    equipo = elegir_de_lista("equipos", empresa.listar_equipos(), describir_equipo)
    proc = elegir_de_lista("procedimientos", empresa.listar_procedimientos(), describir_procedimiento)
    fecha = pedir_fecha("Fecha de las inspecciones")
    semilla = pedir_entero("Semilla (el mismo número repite el mismo caso)")
    prob = pedir_decimal("Probabilidad de defecto (0 a 1, ej: 0.15)", minimo=0, maximo=1)

    inspecciones = Simulador(semilla).simular_lote(empresa, lote, prof, equipo, proc, fecha,
                                                   prob_defecto=prob)
    no_conformes = len(list(filter(lambda m: m.reporte is not None, lote.muestras)))
    print(f"[OK] Se inspeccionaron {len(inspecciones)} muestras con la semilla {semilla}")
    print(f"     No conformes: {no_conformes}/{len(lote.muestras)} "
          f"({lote.porcentaje_no_conforme()}%)")
    print("     Para decidir el lote, usá la opción 'Decidir lote'")


def alertas_calibracion(empresa):
    """Equipos vencidos y próximos a vencer. Usa el árbol AVL de equipos ordenado
    por fecha de calibración (búsquedas por rango)."""
    fecha = pedir_fecha("Fecha de referencia")
    dias = pedir_entero("Avisar los que vencen en los próximos N días", minimo=1)
    vencidos = empresa.equipos_vencidos_al(fecha)
    print(f"\nEquipos VENCIDOS al {fecha}: {len(vencidos)}")
    for equipo in vencidos:
        print(f"  - {describir_equipo(equipo)} (venció el {equipo.fecha_vencimiento})")
    a_vencer = empresa.equipos_que_vencen_entre(fecha, fecha + timedelta(days=dias))
    print(f"Equipos que vencen en los próximos {dias} días: {len(a_vencer)}")
    for equipo in a_vencer:
        print(f"  - {describir_equipo(equipo)} (vence el {equipo.fecha_vencimiento})")
    primero = empresa.equipo_que_vence_primero(fecha)
    if primero is not None:
        print(f"El equipo calibrado que vence primero: {describir_equipo(primero)}, "
              f"el {primero.fecha_vencimiento}")


def reportes_por_fecha(empresa):
    """Reportes de un período, en el orden en que hay que atenderlos: el filtro usa
    el árbol AVL (búsqueda por rango) y el orden, la cola de prioridad (heap)."""
    desde = pedir_fecha("Desde")
    hasta = pedir_fecha("Hasta")
    cola = empresa.cola_atencion_reportes(desde, hasta)   # valida que desde <= hasta
    if cola.esta_vacia():
        print(f"No hay reportes entre {desde} y {hasta}")
        return
    print(f"\n{len(cola)} reporte(s) entre {desde} y {hasta}, en orden de atención "
          f"(primero el más grave):")
    for turno, r in enumerate(cola.en_orden_de_prioridad(), start=1):
        print(f"  {turno}. [{id_corto(r)}] {r.fecha} | gravedad máxima {r.gravedad_maxima}, "
              f"suma {r.suma_gravedades} | {len(r.defectos)} defecto(s)")


# ============================================================
#  MENÚ PRINCIPAL
# ============================================================

OPCIONES = {
    "1": ("Crear lote", crear_lote),
    "2": ("Crear muestras en un lote", crear_muestras),
    "3": ("Registrar profesional", registrar_profesional),
    "4": ("Agregar certificación a un profesional", agregar_certificacion),
    "5": ("Registrar equipo", registrar_equipo),
    "6": ("Crear procedimiento", crear_procedimiento),
    "7": ("Inspeccionar una muestra", inspeccionar),
    "8": ("Ver estado de un lote", ver_lote),
    "9": ("Decidir lote (aprobar / rechazar)", decidir_lote),
    "10": ("Ver reportes de desviación", ver_reportes),
    "11": ("Guardar / cargar / exportar", archivos),
    "12": ("Cargar datos de ejemplo", cargar_datos_ejemplo),
    "13": ("Simulación aleatoria de un lote", simulacion_aleatoria),
    "14": ("Alertas de calibración de equipos", alertas_calibracion),
    "15": ("Reportes por fecha, en orden de atención", reportes_por_fecha),
}


def mostrar_menu(empresa):
    resumen = empresa.resumen()
    print(f"\n{'=' * 60}")
    print("  QUANTUMTECH PRECISION - MONITOREO DE CALIDAD")
    print(f"  Lotes: {resumen['lotes']} | Muestras: {resumen['muestras']} | "
          f"Inspecciones: {resumen['inspecciones']} | Reportes: {len(empresa.reportes())}")
    print(f"{'=' * 60}")
    for clave, (texto, _) in OPCIONES.items():
        print(f"  {clave:>2}. {texto}")
    print("   0. Salir")


def ejecutar_opcion(empresa, opcion):
    """Ejecuta una opción del menú. Retorna la empresa que queda en uso.
    Cualquier error del sistema se muestra y no corta el programa."""
    texto, accion = OPCIONES[opcion]
    print(f"\n--- {texto} ---")
    try:
        resultado = accion(empresa)
    except CalidadError as e:
        # Todas las excepciones propias heredan de CalidadError: un solo except alcanza
        print(f"[X] {type(e).__name__}: {e}")
        return empresa
    except OSError as e:
        # Errores de archivo (no existe, sin permiso) al guardar o cargar
        print(f"[X] Error de archivo: {e}")
        return empresa
    return resultado if isinstance(resultado, Empresa) else empresa


def main():
    empresa = Empresa()
    try:
        while True:
            mostrar_menu(empresa)
            opcion = pedir_texto("\nOpción")
            if opcion == "0":
                break
            if opcion not in OPCIONES:
                print("[X] Opción inválida")
                continue
            empresa = ejecutar_opcion(empresa, opcion)
    except (KeyboardInterrupt, EOFError):
        print()   # Ctrl+C o fin de la entrada: se sale sin mostrar un traceback
    print("Hasta luego.")


if __name__ == "__main__":
    main()
