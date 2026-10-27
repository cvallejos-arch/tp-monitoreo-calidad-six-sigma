"""Página Inspección: datos, observaciones, observaciones al azar y simulación."""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import date

from classes.estado_muestra import EstadoMuestra
from classes.excepciones import CalidadError, DatosInvalidosError
from classes.observacion_dimensional import ObservacionDimensional
from classes.observacion_visual import ObservacionVisual
from classes.proc_visual import ProcedimientoVisual
from classes.simulador import Simulador

from front.estilos import AZUL, BLANCO, COLOR_ESTADO, FONDO_ESTADO, FUENTE, SUAVE, TEXTO
from front.herramientas import Selector, boton, leer_decimal, leer_entero, leer_fecha, tarjeta


class PaginaInspeccion:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

    def _pagina_inspeccion(self, pagina):
        pagina.columnconfigure(0, weight=2, uniform="insp")
        pagina.columnconfigure(1, weight=3, uniform="insp")
        pagina.rowconfigure(0, weight=1)

        # Columna izquierda: datos de la inspección
        marco, f = tarjeta(pagina, "1. Datos de la inspección", "se validan antes de empezar")
        marco.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        f.columnconfigure(1, weight=1)
        self.insp_lote = Selector(f, 30)
        self._campo(f, 0, "Lote", self.insp_lote.combo)
        self.insp_lote.combo.bind("<<ComboboxSelected>>", lambda e: self.refrescar())
        self.insp_muestra = Selector(f, 30)
        self._campo(f, 1, "Muestra", self.insp_muestra.combo)
        boton(f, "Tomar la siguiente de la cola", self.siguiente_de_la_cola, "secundario").grid(
            row=2, column=1, sticky="w", pady=(0, 8))
        self.insp_prof = Selector(f, 30)
        self._campo(f, 3, "Profesional", self.insp_prof.combo)
        self.insp_equipo = Selector(f, 30)
        self._campo(f, 4, "Equipo", self.insp_equipo.combo)
        self.insp_proc = Selector(f, 30)
        self._campo(f, 5, "Procedimiento", self.insp_proc.combo)
        self.insp_proc.combo.bind("<<ComboboxSelected>>", lambda e: self.cambiar_tipo_observacion())
        self.insp_fecha = self._campo(f, 6, "Fecha", ttk.Entry(f))
        self.insp_fecha.insert(0, date.today().isoformat())

        boton(f, "▶   Inspeccionar muestra", self.inspeccionar).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(10, 6))

        # Resultado de la última inspección
        self.resultado_marco = tk.Frame(f, bg="#f6f9fd")
        self.resultado_marco.grid(row=8, column=0, columnspan=2, sticky="ew", pady=4)
        self.resultado = tk.Label(self.resultado_marco, text="Todavía no hay inspecciones",
                                  bg="#f6f9fd", fg=SUAVE, font=(FUENTE, 13, "bold"), anchor="w")
        self.resultado.pack(fill="x", padx=12, pady=(10, 2))
        self.resultado_detalle = tk.Label(self.resultado_marco, text="", bg="#f6f9fd", fg=SUAVE,
                                          font=(FUENTE, 9), anchor="w", justify="left", wraplength=360)
        self.resultado_detalle.pack(fill="x", padx=12, pady=(0, 10))
        self.resultado_marco.bind("<Configure>", lambda e: self.resultado_detalle.configure(
            wraplength=max(e.width - 24, 100)))

        # Simulación: inspecciona todas las muestras pendientes del lote con datos al azar
        boton(f, "🎲   Simulación aleatoria del lote", self.simulacion_aleatoria, "oscuro").grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(10, 2))
        tk.Label(f, text="Usa el lote, profesional, equipo, procedimiento y fecha elegidos",
                 bg=BLANCO, fg=SUAVE, font=(FUENTE, 8)).grid(row=10, column=0, columnspan=2, sticky="w")

        # Columna derecha: observaciones
        marco, f = tarjeta(pagina, "2. Observaciones", "cambian según el procedimiento")
        marco.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        self.form_obs = tk.Frame(f, bg=BLANCO)
        self.form_obs.grid(row=0, column=0, sticky="ew")
        self.obs_desc = tk.StringVar()
        self.obs_detectado = tk.BooleanVar(value=True)
        self.obs_gravedad = tk.StringVar(value="1")
        self.obs_valor = tk.StringVar()
        self.obs_min = tk.StringVar()
        self.obs_max = tk.StringVar()
        self.tipo_obs = None

        botones = tk.Frame(f, bg=BLANCO)
        botones.grid(row=1, column=0, sticky="w", pady=8)
        boton(botones, "+ Agregar observación", self.agregar_observacion, "secundario").pack(side="left")
        boton(botones, "Vaciar lista", self.vaciar_observaciones, "secundario").pack(side="left", padx=8)

        self.tabla_obs = ttk.Treeview(f, columns=("desc", "detalle"), show="headings", height=6)
        self.tabla_obs.heading("desc", text="DESCRIPCIÓN")
        self.tabla_obs.heading("detalle", text="DETALLE")
        self.tabla_obs.column("desc", width=240)
        self.tabla_obs.column("detalle", width=320)
        self.tabla_obs.tag_configure("defecto", background=FONDO_ESTADO["NO_CONFORME"])
        self.tabla_obs.grid(row=2, column=0, sticky="nsew")

        # Observaciones generadas al azar con el Simulador (semilla vacía = distinto cada vez)
        azar = tk.Frame(f, bg="#f6f9fd")
        azar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        tk.Label(azar, text="🎲  Al azar", bg="#f6f9fd", fg=AZUL,
                 font=(FUENTE, 10, "bold")).pack(side="left", padx=(12, 14), pady=8)
        tk.Label(azar, text="Semilla", bg="#f6f9fd", fg=SUAVE, font=(FUENTE, 9)).pack(side="left")
        self.azar_semilla = ttk.Entry(azar, width=8)
        self.azar_semilla.pack(side="left", padx=(4, 12))
        tk.Label(azar, text="Cantidad", bg="#f6f9fd", fg=SUAVE, font=(FUENTE, 9)).pack(side="left")
        self.azar_cantidad = ttk.Entry(azar, width=5)
        self.azar_cantidad.insert(0, "3")
        self.azar_cantidad.pack(side="left", padx=(4, 12))
        boton(azar, "Observaciones al azar", self.observaciones_al_azar).pack(side="right", padx=8, pady=6)
        self.cambiar_tipo_observacion()

    def _es_visual(self):
        try:
            return isinstance(self.insp_proc.elegido("procedimiento"), ProcedimientoVisual)
        except DatosInvalidosError:
            return True

    def cambiar_tipo_observacion(self):
        """Muestra el formulario de observación que corresponde al procedimiento elegido."""
        tipo = "visual" if self._es_visual() else "dimensional"
        if tipo == self.tipo_obs:
            return
        self.tipo_obs = tipo
        self.vaciar_observaciones()
        for hijo in self.form_obs.winfo_children():
            hijo.destroy()
        tk.Label(self.form_obs, text="Descripción", bg=BLANCO, fg=SUAVE,
                 font=(FUENTE, 9)).grid(row=0, column=0, sticky="w")
        ttk.Entry(self.form_obs, textvariable=self.obs_desc, width=46).grid(
            row=0, column=1, columnspan=5, sticky="w", pady=4, padx=(8, 0))
        if tipo == "visual":
            ttk.Checkbutton(self.form_obs, text="Se detectó un defecto",
                            variable=self.obs_detectado).grid(row=1, column=1, sticky="w", padx=(8, 0))
            tk.Label(self.form_obs, text="Gravedad (1 a 5)", bg=BLANCO, fg=SUAVE,
                     font=(FUENTE, 9)).grid(row=1, column=2, padx=(16, 4))
            ttk.Spinbox(self.form_obs, from_=1, to=5, width=4,
                        textvariable=self.obs_gravedad).grid(row=1, column=3, sticky="w")
        else:
            for col, (texto, var) in enumerate((("Valor medido", self.obs_valor),
                                                ("Tol. mínima", self.obs_min),
                                                ("Tol. máxima", self.obs_max))):
                tk.Label(self.form_obs, text=texto, bg=BLANCO, fg=SUAVE, font=(FUENTE, 9)).grid(
                    row=1, column=col * 2, sticky="w", padx=(0 if col == 0 else 8, 4))
                ttk.Entry(self.form_obs, textvariable=var, width=8).grid(
                    row=1, column=col * 2 + 1, sticky="w")

    def agregar_observacion(self):
        try:
            if self.tipo_obs == "visual":
                detectado = self.obs_detectado.get()
                gravedad = leer_entero(self.obs_gravedad.get(), "gravedad") if detectado else None
                obs = ObservacionVisual(self.obs_desc.get(), detectado, gravedad)
            else:
                obs = ObservacionDimensional(leer_decimal(self.obs_valor.get(), "valor medido"),
                                             leer_decimal(self.obs_min.get(), "tolerancia mínima"),
                                             leer_decimal(self.obs_max.get(), "tolerancia máxima"),
                                             self.obs_desc.get())
        except CalidadError as e:
            messagebox.showerror(type(e).__name__, str(e))
            return
        self._sumar_observacion(obs)
        self.obs_desc.set("")

    def _sumar_observacion(self, obs):
        """Agrega una observación a la lista y a la tabla, con un detalle según su tipo."""
        if isinstance(obs, ObservacionVisual):
            hay_defecto = obs.defecto_detectado
            detalle = f"Defecto de gravedad {obs.gravedad}" if hay_defecto else "Sin defecto"
        else:
            hay_defecto = obs.desviacion > 0
            fuera = "FUERA de tolerancia" if hay_defecto else "dentro de tolerancia"
            detalle = f"{obs.valor_medido} en [{obs.tolerancia_min}, {obs.tolerancia_max}] → {fuera}"
        self.observaciones.append(obs)
        self.tabla_obs.insert("", "end", values=(obs.descripcion, detalle),
                              tags=("defecto",) if hay_defecto else ())

    def vaciar_observaciones(self):
        self.observaciones = []
        self.tabla_obs.delete(*self.tabla_obs.get_children())

    def _leer_semilla(self, texto):
        """Semilla vacía = None (un caso distinto cada vez); si no, tiene que ser un entero."""
        texto = (texto or "").strip()
        return None if texto == "" else leer_entero(texto, "semilla")

    def _tolerancias_elegidas(self):
        """Para las dimensionales usa las tolerancias escritas en el formulario, o 9.0 a 10.0."""
        if self.obs_min.get().strip() and self.obs_max.get().strip():
            return (leer_decimal(self.obs_min.get(), "tolerancia mínima"),
                    leer_decimal(self.obs_max.get(), "tolerancia máxima"))
        return 9.0, 10.0

    def observaciones_al_azar(self):
        """Genera observaciones con el Simulador según el procedimiento elegido."""
        def accion():
            proc = self.insp_proc.elegido("procedimiento")
            simulador = Simulador(self._leer_semilla(self.azar_semilla.get()))
            minimo, maximo = self._tolerancias_elegidas()
            return simulador.observaciones_para(
                proc, leer_entero(self.azar_cantidad.get(), "cantidad"),
                tolerancia_min=minimo, tolerancia_max=maximo)
        observaciones = self._ejecutar(accion)
        if observaciones is None:
            return
        for obs in observaciones:
            self._sumar_observacion(obs)
        self.estado.set(f"✔ Se agregaron {len(observaciones)} observaciones al azar")

    def simulacion_aleatoria(self):
        """Inspecciona al azar todas las muestras pendientes del lote elegido."""
        semilla = simpledialog.askstring("Simulación aleatoria",
                                         "Semilla (vacío = al azar):", parent=self.raiz)
        if semilla is None:  # tocó Cancelar
            return
        prob = simpledialog.askstring("Simulación aleatoria",
                                      "Probabilidad de defecto (0 a 1):",
                                      initialvalue="0.2", parent=self.raiz)
        if prob is None:
            return

        def accion():
            lote = self.insp_lote.elegido("lote")
            if lote.siguiente_muestra_pendiente() is None:
                raise DatosInvalidosError("El lote elegido no tiene muestras pendientes")
            simulador = Simulador(self._leer_semilla(semilla))
            minimo, maximo = self._tolerancias_elegidas()
            inspecciones = simulador.simular_lote(
                self.empresa, lote, self.insp_prof.elegido("profesional"),
                self.insp_equipo.elegido("equipo"), self.insp_proc.elegido("procedimiento"),
                leer_fecha(self.insp_fecha.get()),
                prob_defecto=leer_decimal(prob, "probabilidad de defecto"),
                tolerancia_min=minimo, tolerancia_max=maximo)
            return lote, inspecciones
        resultado = self._ejecutar(accion)
        if resultado is None:
            return
        lote, inspecciones = resultado
        muestras = list(map(lambda i: self.empresa.obtener_muestra(i.muestra_id), inspecciones))
        no_conformes = len(list(filter(lambda m: m.estado == EstadoMuestra.NO_CONFORME, muestras)))
        messagebox.showinfo(
            "Simulación aleatoria",
            f"Se inspeccionaron {len(inspecciones)} muestras al azar"
            f"{'' if semilla.strip() == '' else f' (semilla {semilla.strip()})'}.\n\n"
            f"Conformes: {len(inspecciones) - no_conformes}\nNo conformes: {no_conformes}\n\n"
            f"El lote tiene {lote.porcentaje_no_conforme():.1f}% no conforme. "
            f"Decidilo en la página 'Lotes'.")
        self.estado.set(f"✔ Simulación: {len(inspecciones)} muestras inspeccionadas")

    def siguiente_de_la_cola(self, avisar=True):
        try:
            lote = self.insp_lote.elegido("lote")
        except DatosInvalidosError as e:
            messagebox.showerror(type(e).__name__, str(e))
            return
        muestra = lote.siguiente_muestra_pendiente()  # front de la cola
        if muestra is None:
            if avisar:
                messagebox.showinfo("Cola vacía", "Este lote no tiene muestras pendientes")
            return
        self.insp_muestra.combo.set(self._describir_muestra(muestra))

    def inspeccionar(self):
        def accion():
            muestra = self.insp_muestra.elegido("muestra")
            proc = self.insp_proc.elegido("procedimiento")
            if not self.observaciones:
                raise DatosInvalidosError(
                    "Cargá al menos una observación antes de inspeccionar "
                    "(si no hay defectos, agregá una observación sin defecto)."
                )
            # Inspeccion valida todo en su constructor antes de cambiar la muestra
            insp = self.empresa.lanzar_inspeccion(
                muestra, self.insp_prof.elegido("profesional"), self.insp_equipo.elegido("equipo"),
                proc, leer_fecha(self.insp_fecha.get()))
            defectos = insp.ejecutar(self.observaciones)
            insp.cerrar()
            return muestra, proc, defectos
        resultado = self._ejecutar(accion)
        if resultado is None:
            return
        muestra, proc, defectos = resultado
        estado = muestra.estado.value
        fondo, color = FONDO_ESTADO[estado], COLOR_ESTADO[estado]
        self.resultado_marco.configure(bg=fondo)
        self.resultado.configure(text=f"Muestra {estado.replace('_', ' ')}", fg=color, bg=fondo)
        detalle = (f"{len(defectos)} defecto(s) · suma de gravedades {muestra.suma_gravedades()} "
                   f"(límite {proc.limite_gravedad_acumulada}) · "
                   f"{'con' if muestra.tiene_critico() else 'sin'} defecto crítico")
        if muestra.reporte is not None:
            detalle += "\nSe generó un reporte de desviación (página Reportes)."
        self.resultado_detalle.configure(text=detalle, bg=fondo, fg=TEXTO)
        self.vaciar_observaciones()
        self.siguiente_de_la_cola(avisar=False)  # deja elegida la próxima pendiente
        self.estado.set(f"✔ Inspección cerrada: muestra {estado}")