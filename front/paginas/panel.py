"""Página Panel de control: indicadores y gráficos."""

import tkinter as tk
from datetime import date

from classes.equipo import Equipo
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra

from front.estilos import (
    AMARILLO, AZUL, BLANCO, BORDE, CELESTE, COLOR_ESTADO,
    COLOR_GRAVEDAD, FONDO, FUENTE, NARANJA, ROJO, SUAVE,
    TEXTO, VERDE,
)
from front.herramientas import Grafico, id_corto, promedio, tarjeta
from front.visualizaciones import (
    barras_de_progreso, barras_horizontales, barras_verticales, dona, lista_con_insignias, sin_datos,
)


class PaginaPanel:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

    def _pagina_panel(self, pagina):
        pagina.columnconfigure((0, 1, 2), weight=1, uniform="col")
        pagina.rowconfigure((1, 2), weight=1)

        # Fila de indicadores (KPI)
        fila_kpi = tk.Frame(pagina, bg=FONDO)
        fila_kpi.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 6))
        fila_kpi.columnconfigure(tuple(range(6)), weight=1, uniform="kpi")
        self.kpis = {}
        indicadores = (
            ("lotes", "▤", CELESTE, "Lotes"),
            ("avance", "✔", AZUL, "Inspecc."),
            ("no_conforme", "%", ROJO, "No conformes"),
            ("gravedad", "≈", AMARILLO, "Grav. prom."),
            ("criticos", "!", "#b23a64", "Críticos"),
            ("reportes", "⚑", NARANJA, "Reportes"),
        )
        for i, (clave, simbolo, color, titulo) in enumerate(indicadores):
            self.kpis[clave] = self._tarjeta_kpi(fila_kpi, i, simbolo, color, titulo)

        # Gráficos
        graficos = (
            (1, 0, "estado_muestras", "Estado de las muestras", "todas las muestras", 140),
            (1, 1, "gravedad", "Defectos por gravedad", "muestras cerradas · se cuentan con el árbol AVL", 140),
            (1, 2, "lotes", "% no conforme por lote", "de mayor a menor producción (in-orden del árbol AVL)", 140),
            (2, 0, "profesionales", "Inspecciones por profesional", "cantidad y defectos promedio por inspección", 140),
            (2, 1, "equipos", "Calibración de equipos", "árbol AVL por fecha: el que vence primero, arriba", 140),
            (2, 2, "ultimas", "Últimas inspecciones", "las 5 más recientes", 140),
        )
        self.graficos = {}
        for fila, col, clave, titulo, sub, alto in graficos:
            marco, cuerpo = tarjeta(pagina, titulo, sub)
            marco.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)
            self.graficos[clave] = Grafico(cuerpo, alto)
            self.graficos[clave].pack(fill="both", expand=True)

    def _tarjeta_kpi(self, padre, columna, simbolo, color, titulo):
        marco = tk.Frame(padre, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
        marco.grid(row=0, column=columna, sticky="nsew", padx=6, pady=6)
        icono = tk.Canvas(marco, width=38, height=38, bg=BLANCO, highlightthickness=0)
        icono.grid(row=0, column=0, rowspan=3, padx=(10, 8), pady=12)
        icono.create_oval(2, 2, 36, 36, fill=color, outline=color)
        icono.create_text(19, 19, text=simbolo, fill=BLANCO, font=(FUENTE, 13, "bold"))
        valor = tk.Label(marco, text="0", bg=BLANCO, fg=TEXTO, font=(FUENTE, 18, "bold"))
        valor.grid(row=0, column=1, sticky="sw", pady=(12, 0))
        tk.Label(marco, text=titulo, bg=BLANCO, fg=SUAVE, font=(FUENTE, 9)).grid(
            row=1, column=1, sticky="w")
        detalle = tk.Label(marco, text="", bg=BLANCO, fg=color, font=(FUENTE, 8, "bold"))
        detalle.grid(row=2, column=1, sticky="nw", pady=(0, 12))
        return valor, detalle

    def _poner_kpi(self, clave, valor, detalle):
        etiqueta_valor, etiqueta_detalle = self.kpis[clave]
        etiqueta_valor.configure(text=valor)
        etiqueta_detalle.configure(text=detalle)

    def actualizar_panel(self):
        """Calcula los indicadores con los datos de la empresa y redibuja los gráficos."""
        e = self.empresa
        hoy = date.today()
        lotes = e.listar_lotes()
        muestras = e.listar_muestras()
        inspecciones = e.listar_inspecciones()
        reportes = e.reportes()

        cerradas = list(filter(lambda m: m.estado in (EstadoMuestra.CONFORME,
                                                      EstadoMuestra.NO_CONFORME), muestras))
        no_conformes = list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME, cerradas))

        # Defectos por gravedad: usa el árbol AVL de cada lote (clave = gravedad 1 a 5)
        por_gravedad = {g: 0 for g in range(1, 6)}
        for lote in lotes:
            arbol = lote.arbol_defectos_por_gravedad()
            for g in por_gravedad:
                por_gravedad[g] += len(arbol.buscar(g))
        total_defectos = sum(por_gravedad.values())
        gravedad_promedio = (sum(map(lambda g: g * por_gravedad[g], por_gravedad)) / total_defectos
                             if total_defectos else 0)

        # --- Indicadores ---
        contar = lambda estado: len(list(filter(lambda l: l.estado == estado, lotes)))
        self._poner_kpi("lotes", str(len(lotes)),
                        f"{contar(EstadoLote.APROBADO)} ok · {contar(EstadoLote.RECHAZADO)} rech.")
        avance = len(cerradas) / len(muestras) if muestras else 0
        self._poner_kpi("avance", f"{len(cerradas)}/{len(muestras)}", f"{avance:.0%} avance")
        porcentaje = len(no_conformes) / len(cerradas) * 100 if cerradas else 0
        self._poner_kpi("no_conforme", f"{porcentaje:.1f}%",
                        f"{len(no_conformes)} de {len(cerradas)}")
        self._poner_kpi("gravedad", f"{gravedad_promedio:.2f}", f"{total_defectos} defectos")
        self._poner_kpi("criticos", str(por_gravedad[5]), "gravedad 5")
        self._poner_kpi("reportes", str(len(reportes)),
                        f"{len(inspecciones)} insp.")

        # --- Estado de las muestras (dona) ---
        nombres = {"PENDIENTE": "Pendiente", "EN_INSPECCION": "En inspección",
                   "CONFORME": "Conforme", "NO_CONFORME": "No conforme"}
        partes = list(map(lambda est: (nombres[est.value],
                                       len(list(filter(lambda m: m.estado == est, muestras))),
                                       COLOR_ESTADO[est.value]), EstadoMuestra))
        self.graficos["estado_muestras"].mostrar(
            dona(partes, str(len(muestras)), "muestras") if muestras else sin_datos())

        # --- Defectos por gravedad (barras) ---
        self.graficos["gravedad"].mostrar(barras_verticales(
            list(map(lambda g: (f"Grav. {g}", por_gravedad[g], COLOR_GRAVEDAD[g]), por_gravedad))))

        # --- % no conforme por lote, de mayor a menor producción (recorrido in-orden del AVL) ---
        lotes_ordenados = list(reversed(e.arbol_lotes_por_produccion().recorrido_in_orden()))
        datos_lotes = list(map(lambda l: (
            l.nombre_componentes, l.porcentaje_no_conforme(),
            ROJO if l.porcentaje_no_conforme() > 5 else VERDE,
            f"{l.porcentaje_no_conforme():.1f}%"), lotes_ordenados))
        self.graficos["lotes"].mostrar(
            barras_horizontales(datos_lotes, umbral=5, texto_umbral="límite 5 %"))

        # --- Inspecciones por profesional ---
        datos_prof = []
        for prof in e.listar_profesionales():
            propias = e.listar_inspecciones(profesional_id=prof.id)
            if propias:
                defectos_prom = promedio(map(lambda i: len(i.defectos), propias))
                datos_prof.append((prof.nombre, len(propias), CELESTE,
                                   f"{len(propias)} insp · {defectos_prom:.1f} def"))
        datos_prof.sort(key=lambda d: d[1], reverse=True)
        self.graficos["profesionales"].mostrar(
            barras_horizontales(datos_prof, max_filas=5, margen_derecho=104))

        # --- Calibración de equipos: días de validez que les quedan ---
        # equipos_por_calibracion() es el recorrido in-orden del árbol AVL de la
        # empresa: del calibrado hace más tiempo (vence antes) al más reciente.
        dias_validez = Equipo.DIAS_VALIDEZ_CALIBRACION
        filas_equipos = []
        for equipo in e.equipos_por_calibracion():
            restantes = (equipo.fecha_vencimiento - hoy).days
            if not equipo.esta_calibrado(hoy):
                color, texto = ROJO, "VENCIDO"
            else:
                color, texto = (AMARILLO if restantes <= 30 else VERDE), f"{restantes} días"
            filas_equipos.append((f"{equipo.categoria} · {id_corto(equipo.id)}",
                                  min(max(restantes, 0) / dias_validez, 1), color, texto))
        self.graficos["equipos"].mostrar(barras_de_progreso(filas_equipos[:5]))

        # --- Últimas inspecciones ---
        filas = []
        for insp in list(reversed(inspecciones))[:5]:
            muestra = e.obtener_muestra(insp.muestra_id)
            lote = e.obtener_lote(muestra.lote_id)
            filas.append((f"{lote.nombre_componentes} · muestra {id_corto(muestra.id)}",
                          f"{insp.fecha} · {len(insp.defectos)} defecto(s)",
                          muestra.estado.value, COLOR_ESTADO[muestra.estado.value]))
        self.graficos["ultimas"].mostrar(lista_con_insignias(filas))