"""Página Reportes: cola de atención, filtro por fechas, detalle y exportación a JSON."""

import tkinter as tk
from tkinter import filedialog, ttk

from front.estilos import AZUL, BLANCO, FONDO_ESTADO, FUENTE, ROJO, SUAVE, TEXTO
from front.herramientas import boton, leer_fecha, tarjeta, texto_historial


class PaginaReportes:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

    def _pagina_reportes(self, pagina):
        pagina.columnconfigure((0, 1), weight=1, uniform="reportes")
        pagina.rowconfigure(0, weight=1)

        marco, cuerpo = tarjeta(pagina, "Reportes",
                                "en orden de atención (cola de prioridad: el más grave primero) "
                                "· filtro por fechas con el árbol AVL")
        marco.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(1, weight=1)

        # Filtro por período: usa Empresa.reportes_entre (búsqueda por rango en el AVL)
        filtro = tk.Frame(cuerpo, bg=BLANCO)
        filtro.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        tk.Label(filtro, text="Desde", bg=BLANCO, fg=SUAVE, font=(FUENTE, 9)).pack(side="left")
        self.rep_desde = ttk.Entry(filtro, width=11)
        self.rep_desde.pack(side="left", padx=(4, 10))
        tk.Label(filtro, text="Hasta", bg=BLANCO, fg=SUAVE, font=(FUENTE, 9)).pack(side="left")
        self.rep_hasta = ttk.Entry(filtro, width=11)
        self.rep_hasta.pack(side="left", padx=(4, 10))
        boton(filtro, "Filtrar", self.filtrar_reportes, "secundario").pack(side="left")
        boton(filtro, "Ver todos", self.ver_todos_los_reportes, "secundario").pack(side="left", padx=6)
        self._filtro_reportes = None   # None = todos; si no, (desde, hasta)

        columnas = ("turno", "id", "muestra", "fecha", "defectos", "maxima")
        self.tabla_reportes = self._tabla(cuerpo, columnas,
                                          ("TURNO", "REPORTE", "MUESTRA", "FECHA", "DEFECTOS", "GRAV. MÁX."),
                                          10, fila=1)
        for col in columnas:
            self.tabla_reportes.column(col, width=80)
        self.tabla_reportes.column("turno", width=56)
        self.tabla_reportes.tag_configure("critico", background=FONDO_ESTADO["NO_CONFORME"])
        self.tabla_reportes.bind("<<TreeviewSelect>>", lambda e: self.mostrar_reporte())
        boton(cuerpo, "Exportar a JSON", self.exportar_json).grid(row=2, column=0, sticky="e", pady=(10, 0))

        marco, cuerpo = tarjeta(pagina, "Detalle del reporte")
        marco.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.detalle_reporte = tk.Text(cuerpo, wrap="word", font=("Consolas", 10), relief="flat",
                                       background="#f6f9fd", foreground=TEXTO, padx=14, pady=12,
                                       highlightthickness=0)
        self.detalle_reporte.pack(fill="both", expand=True)
        self.detalle_reporte.tag_configure("titulo", font=(FUENTE, 12, "bold"), foreground=AZUL)
        self.detalle_reporte.tag_configure("critico", foreground=ROJO, font=("Consolas", 10, "bold"))

    def filtrar_reportes(self):
        """Muestra solo los reportes entre las dos fechas (los extremos se incluyen)."""
        def accion():
            desde = leer_fecha(self.rep_desde.get())
            hasta = leer_fecha(self.rep_hasta.get())
            self.empresa.reportes_entre(desde, hasta)   # valida que desde <= hasta
            self._filtro_reportes = (desde, hasta)
        self._ejecutar(accion, "Reportes filtrados por fecha")

    def ver_todos_los_reportes(self):
        self._filtro_reportes = None
        self.refrescar()
        self.estado.set("✔ Se muestran todos los reportes")

    def mostrar_reporte(self):
        seleccion = self.tabla_reportes.selection()
        if not seleccion:
            return
        r = self._reportes_por_fila[seleccion[0]]
        t = self.detalle_reporte
        t.delete("1.0", "end")
        t.insert("end", "Reporte de desviación\n\n", "titulo")
        t.insert("end", f"Reporte:      {r.id}\nMuestra:      {r.muestra_id}\nLote:         {r.lote_id}\n"
                        f"Profesional:  {r.profesional_id}\nFecha:        {r.fecha}\n"
                        f"Historial:    {texto_historial(r.historial_estados)}\n\n"
                        f"Defectos ({len(r.defectos)}):\n")
        for d in r.defectos:
            texto = f"  • [{d.tipo}] {d.descripcion} — gravedad {d.gravedad}"
            t.insert("end", texto + (" (CRÍTICO)\n" if d.es_critico() else "\n"),
                     "critico" if d.es_critico() else ())

    def exportar_json(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".json", initialfile="reportes.json",
                                            filetypes=[("JSON", "*.json")])
        if ruta:
            cantidad = self._ejecutar(lambda: self.empresa.exportar_reportes_json(ruta))
            if cantidad is not None:
                self.estado.set(f"✔ Se exportaron {cantidad} reporte(s) a {ruta}")