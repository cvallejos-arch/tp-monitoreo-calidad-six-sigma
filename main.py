

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
)


def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}\n")


def main():
    empresa = Empresa()
    fecha_hoy = date(2025, 6, 15)

    # ============================================================
    #  1. REGISTRAR LOTE Y MUESTRAS
    # ============================================================
    separador("1. REGISTRAR LOTE Y MUESTRAS")

    lote = empresa.crear_registrar_lote("Tornillos", 1000)
    print(f"Lote creado: {lote}")

    # Crear 20 muestras de 50 unidades cada una
    muestras = []
    for i in range(20):
        m = empresa.crear_registrar_muestra(50)
        lote.agregar_muestra(m)
        muestras.append(m)
    print(f"Se agregaron {len(muestras)} muestras al lote")
    print(f"Capacidad usada: {sum(m.cantidad for m in muestras)}/{lote.cantidad_fabricada}")

    # ============================================================
    #  2. REGISTRAR PROFESIONALES CON CERTIFICACIONES
    # ============================================================
    separador("2. REGISTRAR PROFESIONALES CON CERTIFICACIONES")

    prof_ana = empresa.crear_registrar_profesional("Ana")
    cert_iso = Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31))
    prof_ana.agregar_certificacion(cert_iso)
    print(f"Profesional: {prof_ana}")

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
    print(f"Equipo visual: {equipo_visual}")
    print(f"  Calibrado a fecha {fecha_hoy}? {equipo_visual.esta_calibrado(fecha_hoy)}")

    equipo_dimensional = empresa.crear_registrar_equipo(
        "Dimensional", fecha_hoy - timedelta(days=180)
    )
    print(f"Equipo dimensional: {equipo_dimensional}")
    print(f"  Calibrado a fecha {fecha_hoy}? {equipo_dimensional.esta_calibrado(fecha_hoy)}")

    equipo_vencido = empresa.crear_registrar_equipo(
        "Visual", fecha_hoy - timedelta(days=200)
    )
    print(f"Equipo vencido: {equipo_vencido}")
    print(f"  Calibrado a fecha {fecha_hoy}? {equipo_vencido.esta_calibrado(fecha_hoy)}")

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
        categoria_equipo_requerida="Dimensional"
    )
    print(f"Procedimiento dimensional: {proc_dimensional}")

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
        print(f"   Estado muestra: {muestras[0].estado.value} (no cambio)")

    # 5b. Equipo con calibración vencida
    print("\n5b. Intentando inspección con equipo vencido...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_vencido, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")

    # 5c. Equipo de categoría incompatible
    print("\n5c. Intentando inspección con equipo de categoría incompatible...")
    try:
        empresa.lanzar_inspeccion(
            muestras[0], prof_ana, equipo_dimensional, proc_visual, fecha_hoy
        )
    except EquipoNoAptoError as e:
        print(f"   [X] RECHAZADO: {e}")

    # ============================================================
    #  6. EJECUTAR INSPECCIONES VISUALES (POLIMORFISMO)
    # ============================================================
    separador("6. EJECUTAR INSPECCIONES VISUALES")

    # Muestra 0: no conforme (defecto crítico)
    insp_0 = empresa.lanzar_inspeccion(
        muestras[0], prof_ana, equipo_visual, proc_visual, fecha_hoy
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
    print(f"Reporte: {muestras[0].reporte}")

    # Muestras 1 a 18: conformes (sin defectos o leves)
    for i in range(1, 19):
        equipo_i = empresa.crear_registrar_equipo("Visual", fecha_hoy - timedelta(days=50))
        insp = empresa.lanzar_inspeccion(
            muestras[i], prof_ana, equipo_i, proc_visual, fecha_hoy
        )
        obs = [ObservacionVisual("Sin defectos observados", False)]
        insp.ejecutar(obs)
        insp.cerrar()

    print(f"\nMuestras 1-18 inspeccionadas y conformes")

    # ============================================================
    #  7. EJECUTAR INSPECCIÓN DIMENSIONAL (POLIMORFISMO)
    # ============================================================
    separador("7. EJECUTAR INSPECCIÓN DIMENSIONAL")

    # Muestra 19: inspección dimensional
    insp_19 = empresa.lanzar_inspeccion(
        muestras[19], prof_ana, equipo_dimensional, proc_dimensional, fecha_hoy
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

    # ============================================================
    #  8. CONSULTAS DEL LOTE (SIN EFECTOS SECUNDARIOS)
    # ============================================================
    separador("8. CONSULTAS DEL LOTE")

    print(f"Todas cerradas: {lote.todas_cerradas()}")
    print(f"Porcentaje no conforme: {lote.porcentaje_no_conforme()}%")
    print(f"Total defectos críticos: {lote.total_defectos_criticos()}")
    print(f"Conteo por tipo: {lote.conteo_por_tipo()}")

    # ============================================================
    #  9. DECIDIR EL LOTE
    # ============================================================
    separador("9. DECIDIR EL LOTE")

    estado_final = lote.decidir()
    print(f"Decisión del lote: {estado_final.value}")
    print(f"  Muestras no conformes: {sum(1 for m in muestras if m.estado.value == 'NO_CONFORME')}/20")

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
    print(f"\nReportes de desviación generados:")
    for m in muestras:
        if m.reporte is not None:
            r = m.reporte
            print(f"  - Reporte {r.id}:")
            print(f"    Muestra: {r.muestra_id}")
            print(f"    Profesional: {r.profesional_id}")
            print(f"    Fecha: {r.fecha}")
            print(f"    Defectos ({len(r.defectos)}):")
            for d in r.defectos:
                print(f"      - {d}")

    print(f"\n{'='*60}")
    print("  [OK] EJECUCION COMPLETA - TODAS LAS FUNCIONALIDADES DEMOSTRADAS")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()