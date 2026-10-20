"""Menú interactivo del sistema de monitoreo de calidad.
Permite usar el sistema desde la perspectiva de QuantumTech Precision:
registrar lotes, muestras, profesionales, equipos y procedimientos, lanzar
inspecciones, decidir lotes y ver reportes. Ningún error corta el programa:
las excepciones del sistema se atrapan y se muestran como mensaje.
Se corre con: py menu.py"""

from datetime import date, timedelta

from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import CalidadError, DatosInvalidosError



#  FUNCIONES DE ENTRADA (leen y convierten lo que escribe el usuario)


def pedir_texto(mensaje):
    return input(f"{mensaje}: ").strip()


def pedir_entero(mensaje):
    valor = pedir_texto(mensaje)
    try:
        return int(valor)
    except ValueError:
        raise DatosInvalidosError(f"'{valor}' no es un número entero")


def pedir_decimal(mensaje):
    valor = pedir_texto(mensaje).replace(",", ".")
    try:
        return float(valor)
    except ValueError:
        raise DatosInvalidosError(f"'{valor}' no es un número")


def pedir_fecha(mensaje):
    """Pide una fecha AAAA-MM-DD. Enter vacío = fecha de hoy."""
    valor = pedir_texto(f"{mensaje} (AAAA-MM-DD, Enter = hoy)")
    if valor == "":
        return date.today()
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise DatosInvalidosError(f"'{valor}' no es una fecha válida (formato AAAA-MM-DD)")


def pedir_si_no(mensaje):
    return pedir_texto(f"{mensaje} (s/n)").lower() == "s"


def elegir(titulo, opciones, describir):
    """Muestra una lista numerada y devuelve el objeto elegido."""
    if not opciones:
        raise DatosInvalidosError(f"No hay {titulo} cargados todavía")
    print(f"\n{titulo.capitalize()}:")
    for i, obj in enumerate(opciones, start=1):
        print(f"  {i}. {describir(obj)}")
    numero = pedir_entero("Elegí un número")
    if not 1 <= numero <= len(opciones):
        raise DatosInvalidosError(f"Opción fuera de rango: {numero}")
    return opciones[numero - 1]


#  DESCRIPCIONES CORTAS (para no mostrar los UUID completos)

def id_corto(obj):
    return str(obj.id)[:8]


def describir_lote(lote):
    pendientes = len(lote.pendientes_en_orden())
    return (f"{lote.nombre_componentes} [{id_corto(lote)}] - {lote.estado.value} - "
            f"{len(lote.muestras)} muestras ({pendientes} pendientes)")


def describir_muestra(muestra):
    return f"Muestra [{id_corto(muestra)}] - {muestra.cantidad} unidades - {muestra.estado.value}"


def describir_profesional(prof):
    certs = ", ".join(map(lambda c: f"{c.nombre} ({c.fecha_inicio} a {c.fecha_fin})",
                          prof.certificaciones.values()))
    return f"{prof.nombre} - certificaciones: {certs if certs else 'ninguna'}"


def describir_equipo(equipo):
    return f"{equipo.categoria} [{id_corto(equipo)}] - calibrado el {equipo.fecha_calibracion}"


def describir_procedimiento(proc):
    tipo = "Visual" if isinstance(proc, ProcedimientoVisual) else "Dimensional"
    cert = proc.certificacion_requerida or "ninguna"
    return f"{tipo} [{id_corto(proc)}] - límite {proc.limite_gravedad_acumulada} - certificación: {cert}"



#  ACCIONES DEL MENÚ

def crear_lote(empresa):
    nombre = pedir_texto("Nombre de los componentes (ej: Tornillos M8)")
    cantidad = pedir_entero("Cantidad fabricada")
    lote = empresa.crear_registrar_lote(nombre, cantidad)
    print(f"[OK] Lote creado: {describir_lote(lote)}")


def crear_muestras(empresa):
    lote = elegir("lotes", empresa.listar_lotes(), describir_lote)
    cantidad_muestras = pedir_entero("¿Cuántas muestras querés crear?")
    unidades = pedir_entero("Unidades por muestra")
    for _ in range(cantidad_muestras):
        empresa.crear_registrar_muestra(unidades, lote)  # el lote controla la capacidad
    print(f"[OK] Se crearon {cantidad_muestras} muestras. {describir_lote(lote)}")


def registrar_profesional(empresa):
    nombre = pedir_texto("Nombre del profesional (solo letras)")
    prof = empresa.crear_registrar_profesional(nombre)
    print(f"[OK] Profesional registrado: {describir_profesional(prof)}")


def agregar_certificacion(empresa):
    prof = elegir("profesionales", empresa.listar_profesionales(),
                  describir_profesional)
    nombre = pedir_texto("Nombre de la certificación (ej: ISO)")
    inicio = pedir_fecha("Fecha de inicio")
    fin = pedir_fecha("Fecha de fin")
    prof.agregar_certificacion(Certificacion(nombre, inicio, fin))
    print(f"[OK] {describir_profesional(prof)}")


def registrar_equipo(empresa):
    print("Categorías: 1. Visual  2. Dimensional")
    categoria = "Visual" if pedir_entero("Elegí la categoría") == 1 else "Dimensional"
    fecha = pedir_fecha("Fecha de calibración")
    equipo = empresa.crear_registrar_equipo(categoria, fecha)
    print(f"[OK] Equipo registrado: {describir_equipo(equipo)}")
    print(f"     ¿Calibrado hoy? {equipo.esta_calibrado(date.today())} (vale 182 días)")


def crear_procedimiento(empresa):
    print("Tipos: 1. Visual  2. Dimensional")
    tipo = ProcedimientoVisual if pedir_entero("Elegí el tipo") == 1 else ProcedimientoDimensional
    limite = pedir_entero("Límite de gravedad acumulada")
    cert = pedir_texto("Certificación requerida (Enter = ninguna)")
    datos = {"limite_gravedad_acumulada": limite}
    if cert:
        datos["certificacion_requerida"] = cert
    proc = empresa.crear_registrar_procedimiento(tipo, **datos)  # **kwargs
    print(f"[OK] Procedimiento creado: {describir_procedimiento(proc)}")


def cargar_observaciones(procedimiento):
    """Pide las observaciones según el tipo de procedimiento (cada uno recibe las suyas)."""
    observaciones = []
    cantidad = pedir_entero("¿Cuántas observaciones vas a registrar?")
    for i in range(1, cantidad + 1):
        print(f"\n  Observación {i}:")
        descripcion = pedir_texto("  Descripción")
        if isinstance(procedimiento, ProcedimientoVisual):
            if pedir_si_no("  ¿Se detectó un defecto?"):
                gravedad = pedir_entero("  Gravedad (1 a 5)")
                observaciones.append(ObservacionVisual(descripcion, True, gravedad))
            else:
                observaciones.append(ObservacionVisual(descripcion, False))
        else:
            valor = pedir_decimal("  Valor medido")
            minimo = pedir_decimal("  Tolerancia mínima")
            maximo = pedir_decimal("  Tolerancia máxima")
            observaciones.append(ObservacionDimensional(valor, minimo, maximo, descripcion))
    return observaciones


def lanzar_inspeccion(empresa):
    lote = elegir("lotes", empresa.listar_lotes(), describir_lote)
    if pedir_si_no("¿Inspeccionar la siguiente muestra de la cola?"):
        muestra = lote.siguiente_muestra_pendiente()
        if muestra is None:
            print("[X] Este lote no tiene muestras pendientes")
            return
        print(f"Muestra tomada de la cola: {describir_muestra(muestra)}")
    else:
        muestra = elegir("muestras", list(lote.muestras), describir_muestra)

    prof = elegir("profesionales", empresa.listar_profesionales(),
                  describir_profesional)
    equipo = elegir("equipos", empresa.listar_equipos(), describir_equipo)
    proc = elegir("procedimientos", empresa.listar_procedimientos(),
                  describir_procedimiento)
    fecha = pedir_fecha("Fecha de la inspección")

    # Acá Inspeccion valida todo: estado de la muestra, certificación y equipo
    insp = empresa.lanzar_inspeccion(muestra, prof, equipo, proc, fecha)
    print(f"[OK] Inspección iniciada. Estado de la muestra: {muestra.estado.value}")

    defectos = insp.ejecutar(cargar_observaciones(proc))
    print(f"\nDefectos generados: {len(defectos)}")
    for d in defectos:
        print(f"  - {d}")

    insp.cerrar()
    print(f"\n[OK] Muestra cerrada como {muestra.estado.value}")
    print(f"     Suma de gravedades: {muestra.suma_gravedades()} "
          f"(límite {proc.limite_gravedad_acumulada}) | ¿Defecto crítico? {muestra.tiene_critico()}")
    if muestra.reporte is not None:
        print(f"     Se generó un reporte de desviación: {muestra.reporte.id}")


def ver_lote(empresa):
    lote = elegir("lotes", empresa.listar_lotes(), describir_lote)
    print(f"\n{describir_lote(lote)}")
    print(f"Capacidad usada: {sum(map(lambda m: m.cantidad, lote.muestras))}/{lote.cantidad_fabricada}")
    for m in lote.muestras:
        historial = " -> ".join(map(lambda e: e.value, m.historial_estados))
        print(f"  - {describir_muestra(m)} | historial: {historial}")
    print(f"Todas cerradas: {lote.todas_cerradas()}")
    print(f"Porcentaje no conforme: {lote.porcentaje_no_conforme()}%")
    print(f"Defectos críticos: {lote.total_defectos_criticos()} | Por tipo: {lote.conteo_por_tipo()}")


def decidir_lote(empresa):
    lote = elegir("lotes", empresa.listar_lotes(), describir_lote)
    estado = lote.decidir()
    print(f"[OK] Lote {estado.value} ({lote.porcentaje_no_conforme()}% no conforme, máximo 5%)")


def ver_reportes(empresa):
    reportes = empresa.reportes()
    if not reportes:
        print("No hay reportes: todavía no hay muestras no conformes")
        return
    for r in reportes:
        historial = " -> ".join(map(lambda e: e.value, r.historial_estados))
        print(f"\nReporte [{str(r.id)[:8]}] - muestra [{str(r.muestra_id)[:8]}] - fecha {r.fecha}")
        print(f"  Historial: {historial}")
        for d in r.defectos:
            print(f"  - {d}")


def guardar_o_cargar(empresa):
    print("1. Guardar empresa (pickle)  2. Cargar empresa (pickle)  3. Exportar reportes (JSON)")
    opcion = pedir_entero("Elegí una opción")
    if opcion == 1:
        ruta = pedir_texto("Nombre del archivo (ej: empresa.pkl)")
        empresa.guardar(ruta)
        print(f"[OK] Empresa guardada en '{ruta}'")
    elif opcion == 2:
        ruta = pedir_texto("Nombre del archivo (ej: empresa.pkl)")
        empresa = Empresa.cargar(ruta)
        print(f"[OK] Empresa cargada: {empresa.resumen()}")
    elif opcion == 3:
        ruta = pedir_texto("Nombre del archivo (ej: reportes.json)")
        cantidad = empresa.exportar_reportes_json(ruta)
        print(f"[OK] Se exportaron {cantidad} reporte(s) a '{ruta}'")
    return empresa


def cargar_datos_ejemplo(empresa):
    """Carga datos listos para probar el menú sin tipear todo."""
    hoy = date.today()
    lote = empresa.crear_registrar_lote("Tornillos M8", 100)
    for _ in range(5):
        empresa.crear_registrar_muestra(20, lote)

    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", hoy - timedelta(days=30), hoy + timedelta(days=335)))
    empresa.crear_registrar_profesional("Carlos")  # sin certificaciones

    empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=30))
    empresa.crear_registrar_equipo("Dimensional", hoy - timedelta(days=60))
    empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=200))  # vencido

    empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5,
                                          certificacion_requerida="ISO")
    empresa.crear_registrar_procedimiento(ProcedimientoDimensional, limite_gravedad_acumulada=10)
    print("[OK] Datos de ejemplo cargados:")
    print("     1 lote de 100 tornillos con 5 muestras de 20")
    print("     Ana (ISO vigente) y Carlos (sin certificaciones)")
    print("     Equipo visual, equipo dimensional y un equipo visual vencido (200 días)")
    print("     Procedimiento visual (límite 5, pide ISO) y dimensional (límite 10)")



#  MENÚ PRINCIPAL

OPCIONES = {
    "1": ("Crear lote", crear_lote),
    "2": ("Crear muestras en un lote", crear_muestras),
    "3": ("Registrar profesional", registrar_profesional),
    "4": ("Agregar certificación a un profesional", agregar_certificacion),
    "5": ("Registrar equipo", registrar_equipo),
    "6": ("Crear procedimiento", crear_procedimiento),
    "7": ("Lanzar inspección", lanzar_inspeccion),
    "8": ("Ver estado de un lote", ver_lote),
    "9": ("Decidir lote (aprobar / rechazar)", decidir_lote),
    "10": ("Ver reportes de desviación", ver_reportes),
    "11": ("Guardar / cargar / exportar", guardar_o_cargar),
    "12": ("Cargar datos de ejemplo", cargar_datos_ejemplo),
}


def mostrar_menu(empresa):
    print(f"\n{'='*60}")
    print("  QUANTUMTECH PRECISION - MONITOREO DE CALIDAD")
    print(f"{'='*60}")
    resumen = empresa.resumen()
    print(f"  Lotes: {resumen['lotes']} | Muestras: {resumen['muestras']} | "
          f"Inspecciones: {resumen['inspecciones']}")
    print(f"{'-'*60}")
    for clave, (texto, _) in OPCIONES.items():
        print(f"  {clave:>2}. {texto}")
    print("   0. Salir")


def main():
    empresa = Empresa()
    while True:
        mostrar_menu(empresa)
        opcion = pedir_texto("\nOpción")
        if opcion == "0":
            print("Hasta luego.")
            break
        if opcion not in OPCIONES:
            print("[X] Opción inválida")
            continue

        texto, accion = OPCIONES[opcion]
        print(f"\n--- {texto} ---")
        try:
            resultado = accion(empresa)
            if isinstance(resultado, Empresa):  # al cargar un pickle se reemplaza la empresa
                empresa = resultado
        except CalidadError as e:
            # Cualquier error del sistema se muestra y se vuelve al menú
            print(f"[X] {type(e).__name__}: {e}")
        except FileNotFoundError as e:
            print(f"[X] Error: {e}")
        input("\nEnter para volver al menú...")


if __name__ == "__main__":
    main()