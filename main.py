"""Simulación completa (end-to-end) del sistema de monitoreo de calidad:
registra un lote con sus muestras, valida requisitos, ejecuta inspecciones
visuales y dimensionales, decide el lote y muestra reportes y consultas."""

from datetime import date, timedelta

from classes.empresa import Empresa
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.excepciones import (
    TransicionIlegalError,
    CertificacionNoVigenteError,
    EquipoNoAptoError,
    DatosInvalidosError,
    EstructuraVaciaError,
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

    # ============================================================
    #  2. REGISTRAR PROFESIONALES CON CERTIFICACIONES
    # ============================================================
    separador("2. REGISTRAR PROFESIONALES CON CERTIFICACIONES")

    prof_ana = empresa.crear_registrar_profesional("Ana")
    prof_ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
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

    equipo_visual = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=100)
    )
    equipo_dimensional = empresa.crear_registrar_equipo(
        "Dimensional", fecha_hoy - timedelta(days=180)
    )
    equipo_vencido = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=200)
    )

    equipos = {
        "Equipo visual": equipo_visual,
        "Equipo dimensional": equipo_dimensional,
        "Equipo vencido": equipo_vencido,
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

    # ============================================================
    #  5. DEMOSTRAR VALIDACIONES QUE RECHAZAN
    # ============================================================
    separador("5. DEMOSTRAR VALIDACIONES QUE RECHAZAN")

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

    # 5b. Equipo con calibración vencida
    print("\n5b. Intentando inspección con equipo vencido...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_vencido, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")

    # 5c. Equipo de categoría incompatible
    print("\n5c. Intentando inspección con equipo de categoría incompatible...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_dimensional, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")
        print(f"       Detalles del error: {e.detalles}")

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

    # Muestra 19: la última que queda en la cola de pendientes
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
    #  10. RESUMEN FINAL
    # ============================================================
    separador("10. RESUMEN FINAL")

    print(f"Lote: {lote}")
    print("\nReportes de desviación generados:")
    reportes = map(lambda m: m.reporte, filter(lambda m: m.reporte is not None, muestras))
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
    #  11. SERIALIZACIÓN JSON DE LOS REPORTES
    # ============================================================
    separador("11. SERIALIZACIÓN JSON DE LOS REPORTES")

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
    #  12. SERIALIZACIÓN PICKLE DE TODA LA EMPRESA
    # ============================================================
    separador("12. SERIALIZACIÓN PICKLE DE TODA LA EMPRESA")

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

    print(f"\n{'='*60}")
    print("  [OK] EJECUCION COMPLETA - TODAS LAS FUNCIONALIDADES DEMOSTRADAS")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
