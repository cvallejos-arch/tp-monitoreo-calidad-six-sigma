"""Ventana principal: barra lateral, encabezado, páginas y refresco de datos.
App hereda los métodos de cada página (una clase por página, en front/paginas/)."""

import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

from classes.empresa import Empresa
from classes.excepciones import CalidadError, DatosInvalidosError
from classes.proc_visual import ProcedimientoVisual

from front.estilos import (
    AMARILLO, AZUL, BLANCO, CELESTE, FONDO, FONDO_ESTADO,
    FUENTE, LATERAL, LATERAL_ACTIVO, NARANJA, SUAVE, TEXTO,
    VERDE, aplicar_estilos,
)
from front.herramientas import PaginaDesplazable, boton, fecha_larga, id_corto
from front.paginas.archivos import Archivos
from front.paginas.inspeccion import PaginaInspeccion
from front.paginas.lotes import PaginaLotes
from front.paginas.panel import PaginaPanel
from front.paginas.registro import PaginaRegistro
from front.paginas.reportes import PaginaReportes
from front.visualizaciones import contadores


class App(PaginaPanel, PaginaRegistro, PaginaInspeccion, PaginaLotes, PaginaReportes, Archivos):
    PAGINAS = (
        ("panel", "◉   Panel", "Panel de control", "Indicadores del sistema de calidad"),
        ("registro", "✚   Registro", "Registro", "Lotes, muestras, profesionales, equipos y procedimientos"),
        ("inspeccion", "✔   Inspección", "Inspección", "Validar, ejecutar y cerrar inspecciones"),
        ("lotes", "▤   Lotes", "Lotes y muestras", "Estado de cada lote y decisión final"),
        ("reportes", "⚑   Reportes", "Reportes de desviación", "Respaldo de cada muestra no conforme"),
    )

    def __init__(self, raiz):
        self.raiz = raiz
        self.empresa = Empresa()
        self.observaciones = []  # observaciones cargadas para la próxima inspección
        self._lotes_por_fila = {}
        self._reportes_por_fila = {}

        raiz.title("QuantumTech Precision · Monitoreo de Calidad")
        self._poner_icono()
        # La ventana se adapta a la pantalla: maximizada si se puede (Windows),
        # y si no, del tamaño de la pantalla disponible
        ancho = min(1340, raiz.winfo_screenwidth() - 40)
        alto = min(840, raiz.winfo_screenheight() - 80)
        raiz.geometry(f"{ancho}x{alto}+10+10")
        raiz.minsize(1100, 640)
        try:
            raiz.state("zoomed")
        except tk.TclError:
            pass
        raiz.configure(bg=FONDO)
        aplicar_estilos()

        raiz.columnconfigure(1, weight=1)
        raiz.rowconfigure(0, weight=1)
        self._barra_lateral()

        principal = tk.Frame(raiz, bg=FONDO)
        principal.grid(row=0, column=1, sticky="nsew")
        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(1, weight=1)

        # Encabezado: título de la página y fecha
        encabezado = tk.Frame(principal, bg=FONDO)
        encabezado.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 6))
        self.titulo = tk.Label(encabezado, bg=FONDO, fg=TEXTO, font=("Georgia", 22, "bold"))
        self.titulo.pack(side="left")
        self.subtitulo = tk.Label(encabezado, bg=FONDO, fg=SUAVE, font=(FUENTE, 10))
        self.subtitulo.pack(side="left", padx=14, pady=(8, 0))
        tk.Label(encabezado, text=fecha_larga(date.today()), bg=FONDO, fg=TEXTO,
                 font=(FUENTE, 10)).pack(side="right")

        # Páginas (todas en la misma celda; se trae al frente la elegida)
        contenedor = tk.Frame(principal, bg=FONDO)
        contenedor.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 0))
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)
        self.paginas = {}
        for clave, *_ in App.PAGINAS:
            pagina = PaginaDesplazable(contenedor)
            pagina.grid(row=0, column=0, sticky="nsew")
            self.paginas[clave] = pagina
        self._pagina_panel(self.paginas["panel"].interior)
        self._pagina_registro(self.paginas["registro"].interior)
        self._pagina_inspeccion(self.paginas["inspeccion"].interior)
        self._pagina_lotes(self.paginas["lotes"].interior)
        self._pagina_reportes(self.paginas["reportes"].interior)

        # Rueda del mouse: desplaza la página visible (salvo sobre tablas y textos,
        # que tienen su propio desplazamiento)
        raiz.bind_all("<MouseWheel>", lambda e: self._rueda(e, -1 if e.delta > 0 else 1))
        raiz.bind_all("<Button-4>", lambda e: self._rueda(e, -1))   # Linux: rueda arriba
        raiz.bind_all("<Button-5>", lambda e: self._rueda(e, 1))    # Linux: rueda abajo

        # Barra de estado
        self.estado = tk.StringVar()
        tk.Label(principal, textvariable=self.estado, bg=FONDO, fg=AZUL, anchor="w",
                 font=(FUENTE, 9), padx=28, pady=8).grid(row=2, column=0, sticky="ew")

        self.mostrar_pagina("panel")
        self.refrescar()

    def _poner_icono(self):
        """Reemplaza la pluma de tkinter por el logo QT. Usa icono.png (al lado de
        menu.py); si no está, dibuja un círculo azul con los colores de la app."""
        # icono.png está en la carpeta del proyecto, una arriba de front/
        carpeta = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta = os.path.join(carpeta, "icono.png")
        try:
            self._icono = tk.PhotoImage(file=ruta)
        except tk.TclError:
            tamanio = 32
            self._icono = tk.PhotoImage(width=tamanio, height=tamanio)
            centro = (tamanio - 1) / 2
            for y in range(tamanio):
                for x in range(tamanio):
                    distancia = ((x - centro) ** 2 + (y - centro) ** 2) ** 0.5
                    if distancia <= centro - 3:
                        self._icono.put(LATERAL_ACTIVO, (x, y))
                    elif distancia <= centro:
                        self._icono.put("#8fb3e3", (x, y))
        self.raiz.iconphoto(True, self._icono)  # True: también para las ventanas de aviso

    def _barra_lateral(self):
        lateral = tk.Frame(self.raiz, bg=LATERAL, width=230)
        lateral.grid(row=0, column=0, sticky="ns")
        lateral.grid_propagate(False)

        # Logo: círculo con iniciales
        logo = tk.Canvas(lateral, width=86, height=86, bg=LATERAL, highlightthickness=0)
        logo.pack(pady=(30, 10))
        logo.create_oval(3, 3, 83, 83, fill=LATERAL_ACTIVO, outline="#8fb3e3", width=3)
        logo.create_text(43, 43, text="QT", fill=BLANCO, font=(FUENTE, 22, "bold"))
        tk.Label(lateral, text="QuantumTech", bg=LATERAL, fg=BLANCO,
                 font=(FUENTE, 13, "bold")).pack()
        tk.Label(lateral, text="Precision · Calidad", bg=LATERAL, fg="#a9c3e8",
                 font=(FUENTE, 9)).pack(pady=(0, 26))

        self._opciones_menu = {}
        for clave, texto, *_ in App.PAGINAS:
            opcion = tk.Label(lateral, text=texto, bg=LATERAL, fg="#dbe7f7", anchor="w",
                              font=(FUENTE, 11, "bold"), padx=30, pady=11, cursor="hand2")
            opcion.pack(fill="x")
            opcion.bind("<Button-1>", lambda e, c=clave: self.mostrar_pagina(c))
            opcion.bind("<Enter>", lambda e, o=opcion: o.configure(bg=LATERAL_ACTIVO))
            opcion.bind("<Leave>", lambda e, o=opcion, c=clave: o.configure(
                bg=LATERAL_ACTIVO if self._pagina_actual == c else LATERAL))
            self._opciones_menu[clave] = opcion
        self._pagina_actual = None

        # Acciones de archivo, abajo
        abajo = tk.Frame(lateral, bg=LATERAL)
        abajo.pack(side="bottom", fill="x", padx=22, pady=24)
        boton(abajo, "Datos de ejemplo", self.cargar_datos_ejemplo).pack(fill="x", pady=4)
        for texto, accion in (("Guardar empresa", self.guardar_empresa),
                              ("Cargar empresa", self.cargar_empresa)):
            tk.Button(abajo, text=texto, command=accion, bg=LATERAL_ACTIVO, fg=BLANCO,
                      activebackground="#3c78c7", activeforeground=BLANCO, relief="flat",
                      bd=0, cursor="hand2", pady=6, font=(FUENTE, 10)).pack(fill="x", pady=4)

    def mostrar_pagina(self, clave):
        self._pagina_actual = clave
        for c, opcion in self._opciones_menu.items():
            opcion.configure(bg=LATERAL_ACTIVO if c == clave else LATERAL,
                             fg=BLANCO if c == clave else "#dbe7f7")
        _, _, titulo, subtitulo = next(filter(lambda p: p[0] == clave, App.PAGINAS))
        self.titulo.configure(text=titulo)
        self.subtitulo.configure(text=subtitulo)
        self.paginas[clave].tkraise()
        if clave == "panel":
            self.actualizar_panel()

    def _rueda(self, evento, unidades):
        if isinstance(evento.widget, (ttk.Treeview, tk.Text, tk.Listbox)):
            return
        if self._pagina_actual is not None:
            self.paginas[self._pagina_actual].desplazar(unidades)

    def _campo(self, padre, fila, texto, widget):
        tk.Label(padre, text=texto, bg=BLANCO, fg=SUAVE, font=(FUENTE, 9)).grid(
            row=fila, column=0, sticky="w", pady=3, padx=(0, 10))
        widget.grid(row=fila, column=1, sticky="ew", pady=3)
        return widget

    def _ejecutar(self, accion, mensaje_ok=None):
        """Ejecuta una acción del sistema: si lanza una excepción, la muestra."""
        try:
            resultado = accion()
        except (CalidadError, OSError) as e:  # OSError: problemas al leer/escribir archivos
            messagebox.showerror(type(e).__name__, str(e))
            return None
        self.refrescar()
        if mensaje_ok:
            self.estado.set(f"✔ {mensaje_ok}")
        return resultado

    def _tabla(self, padre, columnas, titulos, alto, fila):
        """Crea una tabla con barra de desplazamiento y colores por estado."""
        tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=alto)
        for col, titulo in zip(columnas, titulos):
            tabla.heading(col, text=titulo)
            tabla.column(col, width=110, anchor="center")
        for estado, color in FONDO_ESTADO.items():
            tabla.tag_configure(estado, background=color)
        barra = ttk.Scrollbar(padre, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.grid(row=fila, column=0, sticky="nsew")
        barra.grid(row=fila, column=1, sticky="ns")
        return tabla

    def _describir_muestra(self, m):
        return f"Muestra {id_corto(m.id)} · {m.cantidad} u. · {m.estado.value}"

    def refrescar(self):
        e = self.empresa
        hoy = date.today()
        describir_lote = lambda l: f"{l.nombre_componentes} ({id_corto(l.id)}) · {l.estado.value}"
        describir_prof = lambda p: (f"{p.nombre} ({id_corto(p.id)}) · certificaciones: "
                                    f"{', '.join(p.certificaciones) if p.certificaciones else 'ninguna'}")
        describir_equipo = lambda q: (f"{q.categoria} ({id_corto(q.id)}) · calibrado {q.fecha_calibracion}"
                                      f"{'' if q.esta_calibrado(hoy) else ' · VENCIDO'}")
        describir_proc = lambda p: (f"{'Visual' if isinstance(p, ProcedimientoVisual) else 'Dimensional'} "
                                    f"({id_corto(p.id)}) · límite {p.limite_gravedad_acumulada} · "
                                    f"cert. {p.certificacion_requerida or 'ninguna'}")

        self.muestra_lote.cargar(e.listar_lotes(), describir_lote)
        self.cert_prof.cargar(e.listar_profesionales(), describir_prof)
        self.insp_lote.cargar(e.listar_lotes(), describir_lote)
        self.insp_prof.cargar(e.listar_profesionales(), describir_prof)
        self.insp_equipo.cargar(e.listar_equipos(), describir_equipo)
        self.insp_proc.cargar(e.listar_procedimientos(), describir_proc)
        try:
            lote = self.insp_lote.elegido("lote")
            self.insp_muestra.cargar(list(lote.muestras), self._describir_muestra)
        except DatosInvalidosError:
            self.insp_muestra.cargar([], self._describir_muestra)
        self.cambiar_tipo_observacion()

        # Tabla de lotes (se conserva la selección)
        elegido = self._lote_elegido()
        id_elegido = elegido.id if elegido else None
        self.tabla_lotes.delete(*self.tabla_lotes.get_children())
        self._lotes_por_fila = {}
        for lote in e.listar_lotes():
            fila = self.tabla_lotes.insert("", "end", tags=(lote.estado.value,), values=(
                lote.nombre_componentes, lote.estado.value, lote.cantidad_fabricada,
                len(lote.muestras), len(lote.pendientes_en_orden()),
                f"{lote.porcentaje_no_conforme():.1f}%", lote.total_defectos_criticos()))
            self._lotes_por_fila[fila] = lote
            if lote.id == id_elegido:
                self.tabla_lotes.selection_set(fila)
        self.mostrar_muestras()

        # Tabla de reportes: en el orden en que se atienden (cola de prioridad: el más
        # grave primero) y, si hay un filtro, solo los del período (árbol AVL).
        # En rojo los que tienen un defecto crítico.
        self.tabla_reportes.delete(*self.tabla_reportes.get_children())
        self._reportes_por_fila = {}
        filtro = self._filtro_reportes or (None, None)
        cola = e.cola_atencion_reportes(*filtro)
        for turno, r in enumerate(cola.en_orden_de_prioridad(), start=1):
            fila = self.tabla_reportes.insert(
                "", "end", tags=("critico",) if r.gravedad_maxima == 5 else (),
                values=(turno, id_corto(r.id), id_corto(r.muestra_id), r.fecha,
                        len(r.defectos), r.gravedad_maxima))
            self._reportes_por_fila[fila] = r

        # Resumen del registro (página Registro)
        resumen = e.resumen()
        colores = (CELESTE, AZUL, NARANJA, VERDE, AMARILLO, "#b23a64")
        datos = list(map(lambda par: (par[1][0].capitalize(), par[1][1], colores[par[0] % 6]),
                         enumerate(resumen.items())))
        self.resumen_registro.mostrar(contadores(datos))

        self.estado.set(f"Lotes: {resumen['lotes']}  ·  Muestras: {resumen['muestras']}  ·  "
                        f"Profesionales: {resumen['profesionales']}  ·  Equipos: {resumen['equipos']}  ·  "
                        f"Inspecciones: {resumen['inspecciones']}  ·  Reportes: {len(e.reportes())}")
        if self._pagina_actual == "panel":
            self.actualizar_panel()