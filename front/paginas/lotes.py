"""Página Lotes y muestras: tablas, detalle del lote y decisión."""

from tkinter import messagebox

from front.estilos import AZUL, COLOR_ESTADO, FONDO_ESTADO, FUENTE, ROJO, SUAVE, TEXTO, VERDE
from front.herramientas import (
    Grafico, boton, id_corto, rectangulo_redondeado, tarjeta, texto_historial,
)
from front.visualizaciones import barras_de_progreso, sin_datos


class PaginaLotes:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

    def _pagina_lotes(self, pagina):
        pagina.columnconfigure(0, weight=3)
        pagina.columnconfigure(1, weight=2)
        pagina.rowconfigure(0, weight=2)
        pagina.rowconfigure(1, weight=3)

        marco, cuerpo = tarjeta(pagina, "Lotes", "elegí uno para ver sus muestras")
        marco.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        columnas = ("nombre", "estado", "fabricada", "muestras", "pendientes", "no_conf", "criticos")
        titulos = ("COMPONENTES", "ESTADO", "FABRICADA", "MUESTRAS", "PENDIENTES", "% NO CONF.", "CRÍTICOS")
        self.tabla_lotes = self._tabla(cuerpo, columnas, titulos, 5, fila=0)
        self.tabla_lotes.column("nombre", width=140)
        self.tabla_lotes.column("estado", width=135)
        self.tabla_lotes.bind("<<TreeviewSelect>>", lambda e: self.mostrar_muestras())

        # Detalle del lote elegido
        marco, cuerpo = tarjeta(pagina, "Detalle del lote")
        marco.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.detalle_lote = Grafico(cuerpo, 130)
        self.detalle_lote.pack(fill="both", expand=True)
        boton(cuerpo, "Decidir lote seleccionado", self.decidir_lote).pack(anchor="e", pady=(8, 0))

        marco, cuerpo = tarjeta(pagina, "Muestras del lote", "el historial es la pila de estados")
        marco.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        columnas = ("id", "cantidad", "estado", "defectos", "suma", "historial")
        titulos = ("MUESTRA", "UNIDADES", "ESTADO", "DEFECTOS", "SUMA GRAVEDADES", "HISTORIAL (PILA)")
        self.tabla_muestras = self._tabla(cuerpo, columnas, titulos, 7, fila=0)
        self.tabla_muestras.column("historial", width=420)

    def _lote_elegido(self):
        seleccion = self.tabla_lotes.selection()
        return self._lotes_por_fila.get(seleccion[0]) if seleccion else None

    def mostrar_muestras(self):
        self.tabla_muestras.delete(*self.tabla_muestras.get_children())
        lote = self._lote_elegido()
        if lote is None:
            self.detalle_lote.mostrar(sin_datos("Elegí un lote de la tabla"))
            return
        for m in lote.muestras:
            self.tabla_muestras.insert("", "end", tags=(m.estado.value,), values=(
                id_corto(m.id), m.cantidad, m.estado.value, len(m.defectos),
                m.suma_gravedades(), texto_historial(m.historial_estados)))
        self.detalle_lote.mostrar(self._dibujo_detalle_lote(lote))

    def _dibujo_detalle_lote(self, lote):
        """Avance de inspección, % no conforme contra el 5 % y defectos por tipo."""
        total = len(lote.muestras)
        cerradas = total - len(lote.pendientes_en_orden()) if total else 0
        porcentaje = lote.porcentaje_no_conforme()
        por_tipo = lote.conteo_por_tipo()
        tipos = " · ".join(map(lambda par: f"{par[0].capitalize()}: {par[1]}", por_tipo.items()))
        filas = [
            ("Avance de inspección", cerradas / total if total else 0, AZUL, f"{cerradas}/{total} muestras"),
            ("% no conforme (se rechaza si supera 5 %)", porcentaje / 10,
             ROJO if porcentaje > 5 else VERDE, f"{porcentaje:.1f}%"),
        ]
        barras = barras_de_progreso(filas)

        def dibujar(c, w, h):
            c.create_text(0, 10, text=lote.nombre_componentes, anchor="w", fill=TEXTO,
                          font=(FUENTE, 13, "bold"))
            insignia = lote.estado.value
            ancho = 16 + len(insignia) * 7
            rectangulo_redondeado(c, w - ancho, 0, w, 22, 11, fill=FONDO_ESTADO[insignia], outline="")
            c.create_text(w - ancho / 2, 11, text=insignia, fill=COLOR_ESTADO[insignia],
                          font=(FUENTE, 8, "bold"))
            c.create_text(0, 32, anchor="w", fill=SUAVE, font=(FUENTE, 9),
                          text=f"{lote.cantidad_fabricada} unidades · {lote.total_defectos_criticos()} "
                               f"defecto(s) crítico(s) · {tipos or 'sin defectos'}")
            barras(c, w, h, desde_y=48)  # barras de progreso debajo del encabezado
        return dibujar

    def decidir_lote(self):
        lote = self._lote_elegido()
        if lote is None:
            messagebox.showinfo("Decidir lote", "Seleccioná un lote de la tabla")
            return
        estado = self._ejecutar(lote.decidir)
        if estado:
            messagebox.showinfo("Decisión del lote",
                                f"Lote {estado.value}\n\n{lote.porcentaje_no_conforme():.1f}% de muestras "
                                f"no conformes (se rechaza si supera el 5%)")
            self.estado.set(f"✔ Lote '{lote.nombre_componentes}' {estado.value}")