"""Simulación completa (end-to-end) del sistema de monitoreo de calidad:
registra un lote con sus muestras, valida requisitos, ejecuta inspecciones
visuales y dimensionales, decide el lote y muestra reportes y consultas.
Además provoca a propósito cada error del sistema para mostrar dónde y por
qué se rechaza cada operación. Al final simula lotes con observaciones al
azar usando una semilla, para que cada caso se pueda repetir."""

from datetime import date, timedelta

from classes.empresa import Empresa
from classes.procedimiento import Procedimiento
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.simulador import Simulador
from classes.excepciones import (
    CalidadError,
    TransicionIlegalError,
    CertificacionNoVigenteError,
    EquipoNoAptoError,
    DatosInvalidosError,
    EstructuraVaciaError,
    InspeccionInvalidaError,
)
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra


def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}\n")


def texto_historial(historial):
    """Convierte una secuencia de estados en texto: PENDIENTE -> EN_INSPECCION -> ..."""
    return " -> ".join(map(lambda estado: estado.value, historial))


def inspeccionar(empresa, muestra, profesional, equipo, procedimiento, fecha, observaciones):
    """Lanza, ejecuta y cierra una inspección completa (para no repetir código)."""
    insp = empresa.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)
    insp.ejecutar(observaciones)
    insp.cerrar()
    return insp


def main():
    empresa = Empresa()
    fecha_hoy = date(2025, 6, 15)

    # ============================================================
    #  1. REGISTRAR LOTE Y MUESTRAS (COLA DE PENDIENTES)
    # ============================================================
    separador("1. REGISTRAR LOTE Y MUESTRAS")

    lote = empresa.crear_registrar_lote("Tornillos", 1000)
    print(f"Lote creado: {lote}")

    # Crear 20 muestras de 50 unidades cada una (composicion: el lote crea sus muestras)
    muestras = []
    for i in range(20):
        muestras.append(empresa.crear_registrar_muestra(50, lote))
    print(f"Se crearon {len(muestras)} muestras en el lote")

    capacidad_usada = sum(map(lambda m: m.cantidad, muestras))
    print(f"Capacidad usada: {capacidad_usada}/{lote.cantidad_fabricada}")

    # El lote encola cada muestra al crearla (Cola: primero en entrar, primero en salir)
    print(f"Muestras pendientes en la cola: {len(lote.pendientes_en_orden())}")
    print(f"Siguiente a inspeccionar (front de la cola): {lote.siguiente_muestra_pendiente().id}")  # front: primera en entrar

    # 1a. El lote ya usó sus 1000 unidades: Lote.crear_muestra controla que la
    # suma de las muestras no supere la cantidad fabricada.
    print("\n1a. Intentando crear una muestra más (el lote ya está completo)...")
    try:
        empresa.crear_registrar_muestra(1, lote)
    except TransicionIlegalError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")

    # 1b. validar_cantidad exige un entero mayor a 0.
    print("\n1b. Intentando crear un lote con cantidad 0...")
    try:
        empresa.crear_registrar_lote("Tuercas", 0)
    except DatosInvalidosError as e:
        print(f"   [X] RECHAZADO: {e}")

    # ============================================================
    #  2. REGISTRAR PROFESIONALES CON CERTIFICACIONES
    # ============================================================
    separador("2. REGISTRAR PROFESIONALES CON CERTIFICACIONES")

    prof_ana = empresa.crear_registrar_profesional("Ana")
    prof_ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    # Seguridad está vencida desde 2023: la usamos en el caso 5b
    prof_ana.agregar_certificacion(Certificacion("Seguridad", date(2023, 1, 1), date(2023, 12, 31)))
    print(f"Profesional: {prof_ana}")

    vigentes = prof_ana.certificaciones_vigentes(fecha_hoy)
    nombres_vigentes = ", ".join(map(lambda c: c.nombre, vigentes))
    print(f"  Certificaciones vigentes al {fecha_hoy}: {nombres_vigentes}")

    prof_carlos = empresa.crear_registrar_profesional("Carlos")
    # Carlos NO tiene certificación ISO
    print(f"Profesional: {prof_carlos}")

    # ============================================================
    #  3. REGISTRAR EQUIPOS CALIBRADOS
    # ============================================================
    separador("3. REGISTRAR EQUIPOS CALIBRADOS")

    # Equipo.esta_calibrado acepta de 0 a 182 días entre la calibración y la
    # inspección, contando los extremos. Probamos los dos lados del borde.
    equipo_visual = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=100)
    )
    equipo_borde = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=182)
    )
    equipo_dimensional = empresa.crear_registrar_equipo(
        "Dimensional", fecha_hoy - timedelta(days=180)
    )
    equipo_vencido = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=183)
    )

    equipos = {
        "Equipo visual (100 días)": equipo_visual,
        "Equipo en el borde (182 días)": equipo_borde,
        "Equipo dimensional (180 días)": equipo_dimensional,
        "Equipo vencido (183 días)": equipo_vencido,
    }
    for nombre, equipo in equipos.items():
        print(f"{nombre}: {equipo}")
        print(f"  Calibrado a fecha {fecha_hoy}? {equipo.esta_calibrado(fecha_hoy)}")

    # ============================================================
    #  4. CREAR PROCEDIMIENTOS (POLIMORFISMO)
    # ============================================================
    separador("4. CREAR PROCEDIMIENTOS (POLIMORFISMO)")

    # Usando **kwargs via Empresa
    proc_visual = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual,
        limite_gravedad_acumulada=5,
        categoria_equipo_requerida="Visual",
        certificacion_requerida="ISO"
    )
    print(f"Procedimiento visual (con cert ISO): {proc_visual}")

    proc_dimensional = empresa.crear_registrar_procedimiento(
        ProcedimientoDimensional,
        limite_gravedad_acumulada=10,
        unidad_medida="mm"
    )
    print(f"Procedimiento dimensional: {proc_dimensional} (unidad: {proc_dimensional.unidad_medida})")

    # Procedimiento que pide la certificación de Seguridad (para el caso 5b)
    proc_seguridad = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual,
        limite_gravedad_acumulada=5,
        certificacion_requerida="Seguridad"
    )
    print(f"Procedimiento visual (con cert Seguridad): {proc_seguridad}")

    # 4a. Procedimiento es abstracta (ABC con evaluar() abstracto): Python no deja
    # crearla. Es un TypeError de Python, no una excepción nuestra.
    print("\n4a. Intentando crear un Procedimiento genérico (clase abstracta)...")
    try:
        Procedimiento(limite_gravedad_acumulada=5, categoria_equipo_requerida="Visual")
    except TypeError as e:
        print(f"   [X] RECHAZADO: {e}")

    # ============================================================
    #  5. DEMOSTRAR VALIDACIONES QUE RECHAZAN
    # ============================================================
    separador("5. DEMOSTRAR VALIDACIONES QUE RECHAZAN")

    # Todas estas validaciones están en el constructor de Inspeccion y se hacen
    # ANTES de iniciar la inspección: si fallan, la muestra no cambia de estado.

    # 5a. Profesional sin certificación requerida
    print("5a. Intentando inspección con profesional sin certificación...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_carlos, equipo_visual, proc_visual, fecha_hoy
        )
    except CertificacionNoVigenteError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")
        print(f"   Estado muestra: {muestras[0].estado.value} (no cambio)")

    # 5b. Ana tiene la certificación de Seguridad, pero venció en 2023
    print("\n5b. Intentando inspección con certificación vencida...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_visual, proc_seguridad, fecha_hoy
        )
    except CertificacionNoVigenteError as e:
        print(f"   [X] RECHAZADO: {e}")

    # 5c. Equipo calibrado hace 183 días (uno más que el máximo)
    print("\n5c. Intentando inspección con equipo vencido...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_vencido, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")

    # 5d. Equipo de categoría incompatible
    print("\n5d. Intentando inspección con equipo de categoría incompatible...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_dimensional, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")

    # 5e. Fallan dos cosas a la vez (certificación y equipo). El constructor
    # valida en orden: fecha, estado de la muestra, certificación, compatibilidad,
    # calibración. Por eso sale solo el primer error.
    print("\n5e. Intentando inspección que falla por certificación Y por equipo...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_carlos, equipo_vencido, proc_visual, fecha_hoy
        )
    except CalidadError as e:
        print(f"   [X] RECHAZADO con {type(e).__name__}: {e}")

    # 5f. Observación con gravedad fuera del rango 1 a 5
    print("\n5f. Intentando crear una observación con gravedad 6...")
    try:
        ObservacionVisual("Raya profunda", True, 6)
    except DatosInvalidosError as e:
        print(f"   [X] RECHAZADO: {e}")

    print(f"\nDespués de todos los intentos, la muestra 0 sigue: {muestras[0].estado.value}")

    # ============================================================
    #  6. EJECUTAR INSPECCIONES VISUALES (POLIMORFISMO + COLA)
    # ============================================================
    separador("6. EJECUTAR INSPECCIONES VISUALES")

    # Muestra 0: no conforme (defecto crítico). Se toma del frente de la cola.
    insp_0 = empresa.lanzar_siguiente_inspeccion(  # toma la muestra del front de la cola (FIFO)
        lote, prof_ana, equipo_visual, proc_visual, fecha_hoy
    )
    obs_visual_0 = [
        ObservacionVisual("Fractura completa en pieza", True, 5),
        ObservacionVisual("Decoloración leve", True, 1),
    ]
    defectos_0 = insp_0.ejecutar(obs_visual_0)
    print(f"Muestra 0 — Defectos encontrados: {len(defectos_0)}")
    for d in defectos_0:
        print(f"  - {d}")
    insp_0.cerrar()
    print(f"Estado muestra 0: {muestras[0].estado.value}")
    print(f"Historial de estados (pila): {texto_historial(muestras[0].historial_estados)}")  # del bottom al top
    print(f"Reporte: {muestras[0].reporte}")

    # 6a. La muestra 0 ya está cerrada: no puede tener otra inspección
    print("\n6a. Intentando inspeccionar de nuevo la muestra 0...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_visual, proc_visual, fecha_hoy
        )
    except TransicionIlegalError as e:
        print(f"   [X] RECHAZADO: {e}")

    # 6b. Una inspección cerrada no se puede volver a ejecutar ni cerrar
    print("\n6b. Intentando ejecutar una inspección ya cerrada...")
    try:
        insp_0.ejecutar([ObservacionVisual("Raya", True, 1)])
    except InspeccionInvalidaError as e:
        print(f"   [X] RECHAZADO: {e}")

    print("\n6c. Intentando cerrar dos veces la misma inspección...")
    try:
        insp_0.cerrar()
    except InspeccionInvalidaError as e:
        print(f"   [X] RECHAZADO: {e}")

    # 6d. Muestra.agregar_defecto solo funciona con la muestra EN_INSPECCION
    print("\n6d. Intentando agregar un defecto a una muestra ya cerrada...")
    try:
        muestras[0].agregar_defecto(defectos_0[0])
    except TransicionIlegalError as e:
        print(f"   [X] RECHAZADO: {e}")

    # 6e. Lote.decidir exige que todas las muestras estén cerradas
    print("\n6e. Intentando decidir el lote con 19 muestras todavía pendientes...")
    try:
        lote.decidir()
    except TransicionIlegalError as e:
        print(f"   [X] RECHAZADO: {e}")

    # Muestras 1 a 18: conformes. La cola entrega las pendientes en orden de creación.
    for i in range(1, 19):
        insp = empresa.lanzar_siguiente_inspeccion(  # toma la muestra del front de la cola (FIFO)
            lote, prof_ana, equipo_visual, proc_visual, fecha_hoy
        )
        insp.ejecutar([ObservacionVisual("Sin defectos observados", False)])
        insp.cerrar()

    print("\nMuestras 1-18 inspeccionadas en orden de la cola y conformes")
    print(f"Muestras pendientes en la cola: {len(lote.pendientes_en_orden())}")

    # ============================================================
    #  7. EJECUTAR INSPECCIÓN DIMENSIONAL (POLIMORFISMO)
    # ============================================================
    separador("7. EJECUTAR INSPECCIÓN DIMENSIONAL")

    # Muestra 19: la última que queda en la cola de pendientes.
    # La gravedad se calcula según cuánto se pasa de la tolerancia
    # (exceso = desviación / rango): 0.5 -> gravedad 2, 1.0 -> gravedad 3.
    insp_19 = empresa.lanzar_siguiente_inspeccion(  # toma la muestra del front de la cola (FIFO)
        lote, prof_ana, equipo_dimensional, proc_dimensional, fecha_hoy
    )
    obs_dim = [
        ObservacionDimensional(10.5, 9.0, 10.0, "Pieza fuera de tolerancia superior"),
        ObservacionDimensional(9.5, 9.0, 10.0, "Pieza dentro de tolerancia"),
        ObservacionDimensional(8.0, 9.0, 10.0, "Pieza fuera de tolerancia inferior"),
    ]
    defectos_19 = insp_19.ejecutar(obs_dim)
    print(f"Muestra 19 — Defectos dimensionales: {len(defectos_19)}")
    for d in defectos_19:
        print(f"  - {d}")
    insp_19.cerrar()
    print(f"Suma de gravedades: {muestras[19].suma_gravedades()} (límite 10)")
    print(f"Estado muestra 19: {muestras[19].estado.value}")

    print("\nIntentando inspeccionar con la cola de pendientes vacía...")
    try:
        empresa.lanzar_siguiente_inspeccion(
            lote, prof_ana, equipo_visual, proc_visual, fecha_hoy
        )
    except EstructuraVaciaError as e:
        print(f"   [X] RECHAZADO: {e}")

    # ============================================================
    #  8. CONSULTAS DEL LOTE (SIN EFECTOS SECUNDARIOS)
    # ============================================================
    separador("8. CONSULTAS DEL LOTE")

    print(f"Todas cerradas: {lote.todas_cerradas()}")
    print(f"Porcentaje no conforme: {lote.porcentaje_no_conforme()}%")
    print(f"Total defectos críticos: {lote.total_defectos_criticos()}")
    print("Conteo por tipo:")
    for tipo, cantidad in lote.conteo_por_tipo().items():
        print(f"  - {tipo}: {cantidad}")

    # ============================================================
    #  9. DECIDIR EL LOTE
    # ============================================================
    separador("9. DECIDIR EL LOTE")

    # 1 no conforme de 20 = 5 % exacto. La regla rechaza solo si supera el 5 %.
    estado_final = lote.decidir()
    print(f"Decisión del lote: {estado_final.value}")

    no_conformes = list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME, muestras))
    print(f"  Muestras no conformes: {len(no_conformes)}/{len(muestras)}")

    # Intentar decidir de nuevo
    print("\nIntentando decidir el lote de nuevo...")
    try:
        lote.decidir()
    except TransicionIlegalError as e:
        print(f"   [X] RECHAZADO (decision final): {e}")

    # ============================================================
    #  10. SEGUNDO LOTE: REGLAS DE CIERRE Y LOTE RECHAZADO
    # ============================================================
    separador("10. SEGUNDO LOTE: REGLAS DE CIERRE Y LOTE RECHAZADO")

    # Muestra.cerrar marca NO_CONFORME si hay un defecto de gravedad 5
    # o si la suma de gravedades SUPERA el límite (5 en el procedimiento visual).
    lote_2 = empresa.crear_registrar_lote("Arandelas", 40)
    m_igual = empresa.crear_registrar_muestra(10, lote_2)
    m_supera = empresa.crear_registrar_muestra(10, lote_2)
    m_critica = empresa.crear_registrar_muestra(10, lote_2)
    m_limpia = empresa.crear_registrar_muestra(10, lote_2)

    # 10a. Suma igual al límite (2 + 3 = 5): queda CONFORME porque la regla es "supera"
    inspeccionar(empresa, m_igual, prof_ana, equipo_borde, proc_visual, fecha_hoy,
                 [ObservacionVisual("Raya superficial", True, 2),
                  ObservacionVisual("Mancha", True, 3)])
    print(f"10a. Suma igual al límite ({m_igual.suma_gravedades()} = 5): {m_igual.estado.value}")
    print("     (usamos el equipo calibrado hace 182 días: el borde se acepta)")

    # 10b. Suma mayor al límite (3 + 3 = 6) sin ningún defecto crítico
    inspeccionar(empresa, m_supera, prof_ana, equipo_visual, proc_visual, fecha_hoy,
                 [ObservacionVisual("Raya", True, 3),
                  ObservacionVisual("Abolladura", True, 3)])
    print(f"10b. Suma mayor al límite ({m_supera.suma_gravedades()} > 5): {m_supera.estado.value}")

    # 10c. Un solo defecto crítico: alcanza para que sea NO_CONFORME
    inspeccionar(empresa, m_critica, prof_ana, equipo_visual, proc_visual, fecha_hoy,
                 [ObservacionVisual("Fisura completa", True, 5)])
    print(f"10c. Un defecto crítico (gravedad 5): {m_critica.estado.value}")

    # 10d. Sin defectos: CONFORME y sin reporte
    inspeccionar(empresa, m_limpia, prof_ana, equipo_visual, proc_visual, fecha_hoy,
                 [ObservacionVisual("Sin defectos observados", False)])
    print(f"10d. Sin defectos: {m_limpia.estado.value} | Reporte: {m_limpia.reporte}")

    # 10e. 2 no conformes de 4 = 50 %: supera el 5 %, el lote se rechaza
    print(f"\nPorcentaje no conforme del lote 2: {lote_2.porcentaje_no_conforme()}%")
    print(f"Decisión del lote 2: {lote_2.decidir().value}")

    # ============================================================
    #  11. RESUMEN FINAL
    # ============================================================
    separador("11. RESUMEN FINAL")

    print(f"Lote: {lote}")
    print(f"Lote 2: {lote_2}")
    print("\nReportes de desviación generados:")
    reportes = empresa.reportes()
    for r in reportes:
        print(f"  - Reporte {r.id}:")
        print(f"    Muestra: {r.muestra_id}")
        print(f"    Profesional: {r.profesional_id}")
        print(f"    Fecha: {r.fecha}")
        print(f"    Historial: {texto_historial(r.historial_estados)}")
        print(f"    Defectos ({len(r.defectos)}):")
        for d in r.defectos:
            print(f"      - {d}")

    print("\nConsultas dinámicas en Empresa con **kwargs (filtros):")
    lotes_aprobados = empresa.listar_lotes(estado=EstadoLote.APROBADO)
    print(f"  - Lotes con estado APROBADO: {len(lotes_aprobados)}")
    lotes_rechazados = empresa.listar_lotes(estado=EstadoLote.RECHAZADO)
    print(f"  - Lotes con estado RECHAZADO: {len(lotes_rechazados)}")
    muestras_no_conf = empresa.listar_muestras(estado=EstadoMuestra.NO_CONFORME)
    print(f"  - Muestras con estado NO_CONFORME: {len(muestras_no_conf)}")
    inspecciones_cerradas = empresa.listar_inspecciones(cerrada=True)
    print(f"  - Inspecciones cerradas: {len(inspecciones_cerradas)}")

    print("\nIntentando filtrar por un atributo inexistente...")
    try:
        empresa.listar_lotes(estdo=EstadoLote.APROBADO)
    except DatosInvalidosError as e:
        print(f"   [X] RECHAZADO: {e}")

    print("\nResumen del registro de la empresa:")
    for categoria, cantidad in empresa.resumen().items():
        print(f"  - {categoria}: {cantidad}")

    # ============================================================
    #  12. SERIALIZACIÓN JSON DE LOS REPORTES
    # ============================================================
    separador("12. SERIALIZACIÓN JSON DE LOS REPORTES")

    ruta_json = "reportes.json"
    cantidad = empresa.exportar_reportes_json(ruta_json)  # to_dict() + json.dump
    print(f"Se exportaron {cantidad} reporte(s) a '{ruta_json}' (archivo legible)")

    reportes_cargados = Empresa.cargar_reportes_json(ruta_json)  # json.load + Clase(**data)
    for r in reportes_cargados:
        print(f"  - Reporte cargado: {r}")
        print(f"    Defectos: {list(map(lambda d: d.descripcion, r.defectos))}")

    iguales = all(map(
        lambda par: par[0].to_dict() == par[1].to_dict(),
        zip(empresa.reportes(), reportes_cargados)
    ))
    print(f"Los reportes cargados coinciden con los originales: {iguales}")

    # ============================================================
    #  13. SERIALIZACIÓN PICKLE DE TODA LA EMPRESA
    # ============================================================
    separador("13. SERIALIZACIÓN PICKLE DE TODA LA EMPRESA")

    ruta_pkl = "empresa.pkl"
    empresa.guardar(ruta_pkl)  # pickle.dump con "wb"
    print(f"Empresa completa guardada en '{ruta_pkl}' (archivo binario)")

    empresa_cargada = Empresa.cargar(ruta_pkl)  # pickle.load con "rb"
    print(f"Empresa cargada. ¿Es otro objeto? {empresa_cargada is not empresa}")
    print(f"¿Mismo contenido? {empresa_cargada.resumen() == empresa.resumen()}")

    lote_cargado = empresa_cargada.obtener_lote(lote.id)
    print(f"Lote recuperado: estado {lote_cargado.estado.value}, "
          f"{len(lote_cargado.muestras)} muestras")
    muestra_0 = empresa_cargada.obtener_muestra(muestras[0].id)
    print(f"Historial de la muestra 0 recuperado: {texto_historial(muestra_0.historial_estados)}")

    # ============================================================
    #  14. SIMULACIÓN ALEATORIA (CON SEMILLA)
    # ============================================================
    separador("14. SIMULACIÓN ALEATORIA (CON SEMILLA)")

    # El Simulador inventa las observaciones al azar; las reglas del dominio no
    # cambian. Con la misma semilla se repite exactamente el mismo caso.
    print("Ejemplo: 5 observaciones visuales al azar con la semilla 7 "
          "(probabilidad de defecto 0.5):")
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

    print("\nLote de 20 muestras, probabilidad de defecto 0.15, límite de gravedad 5:")
    lotes_simulados = {}
    for semilla in (5, 1):
        lote_sim = simular(semilla)
        no_conf = len(list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME,
                                  lote_sim.muestras)))
        porcentaje = lote_sim.porcentaje_no_conforme()
        print(f"  Semilla {semilla}: {no_conf}/20 no conformes ({porcentaje}%) "
              f"-> {lote_sim.decidir().value}")
        lotes_simulados[semilla] = lote_sim
    print("  (semilla 5: exactamente 5 % se aprueba; semilla 1: 10 % supera el 5 % y se rechaza)")

    # Reproducibilidad: misma semilla, mismos estados muestra por muestra
    repetido = simular(5)
    estados = lambda lote_x: list(map(lambda m: m.estado, lote_x.muestras))
    print(f"\nRepitiendo la semilla 5: ¿mismo resultado muestra por muestra? "
          f"{estados(repetido) == estados(lotes_simulados[5])}")

    # La simulación respeta las validaciones: Carlos no tiene la certificación ISO
    print("\n14a. Intentando simular con un profesional sin certificación...")
    lote_carlos = empresa.crear_registrar_lote("Remaches", 10)
    empresa.crear_registrar_muestra(10, lote_carlos)
    try:
        Simulador(1).simular_lote(empresa, lote_carlos, prof_carlos, equipo_visual,
                                  proc_visual, fecha_hoy)
    except CertificacionNoVigenteError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"   La muestra sigue {lote_carlos.muestras[0].estado.value}: "
              f"se validó antes de iniciar la inspección")

    # ============================================================
    #  15. RECURSIVIDAD Y ÁRBOLES BINARIOS (UNIDADES 7 Y 8 EDP)
    # ============================================================
    separador("15. RECURSIVIDAD Y ÁRBOLES BINARIOS DE BÚSQUEDA")

    # 15.1 Recursividad sobre ListaEnlazada (Unidad 7)
    print("15.1 Métodos recursivos sobre ListaEnlazada:")
    from classes.lista_enlazada import ListaEnlazada
    lista_demo = ListaEnlazada()
    for val in [10, 25, 5, 25, 40]:
        lista_demo.insertar_final(val)
    print(f"  Lista original: {lista_demo}")
    print(f"  Longitud calculada recursivamente: {lista_demo.longitud_recursiva()}")
    print(f"  Buscar recursivo 25: {lista_demo.buscar_recursivo(25)}")
    print(f"  Buscar recursivo 99: {lista_demo.buscar_recursivo(99)}")
    print(f"  Contar recursivo apariciones de 25: {lista_demo.contar_recursivo(25)}")
    print(f"  Conversión a lista estándar recursiva: {lista_demo.a_lista_recursiva()}")
    lista_demo.invertir_recursivo()
    print(f"  Lista invertida recursivamente: {lista_demo}")

    # 15.2 Árbol Binario de Búsqueda indexando el dominio (Unidad 8)
    print("\n15.2 Árbol Binario de Búsqueda (ABB) indexando defectos por gravedad:")
    arbol_defectos = lote.arbol_defectos_por_gravedad()
    print(f"  Árbol creado: {arbol_defectos}")
    print(f"  Altura del árbol: {arbol_defectos.altura()}")
    print(f"  Defectos ordenados por gravedad (recorrido in-orden):")
    for d in arbol_defectos.recorrido_in_orden():
        print(f"    - [{d.tipo}] {d.descripcion} (gravedad {d.gravedad})")

    criticos = arbol_defectos.buscar_todos(5)
    print(f"  Búsqueda rápida de defectos críticos (gravedad 5) en el árbol: {len(criticos)} encontrados")

    # Árbol de lotes por producción
    print("\n15.3 Árbol Binario de Búsqueda de Lotes por Volumen de Producción:")
    arbol_lotes = empresa.arbol_lotes_por_produccion()
    print(f"  Lote con menor producción (mínimo del árbol): {arbol_lotes.minimo().nombre_componentes} ({arbol_lotes.minimo().cantidad_fabricada} un.)")
    print(f"  Lote con mayor producción (máximo del árbol): {arbol_lotes.maximo().nombre_componentes} ({arbol_lotes.maximo().cantidad_fabricada} un.)")
    print("  Recorrido in-orden de lotes por producción creciente:")
    for l in arbol_lotes.recorrido_in_orden():
        print(f"    - {l.nombre_componentes}: {l.cantidad_fabricada} piezas")

    print(f"\n{'='*60}")
    print("  [OK] EJECUCION COMPLETA - TODAS LAS FUNCIONALIDADES DEMOSTRADAS")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()