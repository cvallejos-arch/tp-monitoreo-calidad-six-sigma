"""Interfaz gráfica del sistema de monitoreo de calidad (QuantumTech Precision).
Usa tkinter, que viene incluido con Python: no hay que instalar nada.
Toda la lógica está en las clases del TP; esta ventana solo las usa.
Cuando una operación no se puede hacer, la excepción del sistema se muestra
en una ventana de error y el programa sigue funcionando.
Se corre con: py app.py"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import CalidadError, DatosInvalidosError


# Colores de la interfaz
AZUL = "#1e3a5f"
AZUL_CLARO = "#e8eef6"
FONDO = "#f5f7fa"
COLORES_ESTADO = {
    "PENDIENTE": "#eceff1",
    "EN_INSPECCION": "#fff4cc",
    "CONFORME": "#d7f2dd",
    "NO_CONFORME": "#f8d7da",
    "EN_PRODUCCION": "#eceff1",
    "APROBADO": "#d7f2dd",
    "RECHAZADO": "#f8d7da",
}


def id_corto(obj_id):
    return str(obj_id)[:8]


def leer_fecha(texto):
    try:
        return date.fromisoformat(texto.strip())
    except ValueError:
        raise DatosInvalidosError(f"'{texto}' no es una fecha válida (formato AAAA-MM-DD)")


def leer_entero(texto, campo):
    try:
        return int(texto.strip())
    except ValueError:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser un número entero")


def leer_decimal(texto, campo):
    try:
        return float(texto.strip().replace(",", "."))
    except ValueError:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser un número")


class Selector:
    """Combobox que muestra textos pero devuelve el objeto elegido."""

    def __init__(self, padre, ancho=45):
        self._opciones = {}
        self.combo = ttk.Combobox(padre, state="readonly", width=ancho)

    def cargar(self, objetos, describir):
        textos = list(map(describir, objetos))
        self._opciones = dict(zip(textos, objetos))
        actual = self.combo.get()
        self.combo["values"] = textos
        if actual not in self._opciones:
            self.combo.set(textos[0] if textos else "")

    def elegido(self, nombre):
        texto = self.combo.get()
        if texto not in self._opciones:
            raise DatosInvalidosError(f"Elegí un/a {nombre}")
        return self._opciones[texto]


class App:
    def __init__(self, raiz):
        self.raiz = raiz
        self.empresa = Empresa()
        self.observaciones = []  # observaciones cargadas para la próxima inspección

        raiz.title("QuantumTech Precision - Monitoreo de Calidad")
        raiz.geometry("1180x740")
        raiz.configure(bg=FONDO)
        self._estilos()

        # Encabezado
        encabezado = tk.Frame(raiz, bg=AZUL, height=60)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text="QuantumTech Precision", bg=AZUL, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(encabezado, text="Sistema de monitoreo de calidad", bg=AZUL, fg="#b8c7dc",
                 font=("Segoe UI", 11)).pack(side="left", pady=12)
        for texto, accion in (("Cargar empresa", self.cargar_empresa),
                              ("Guardar empresa", self.guardar_empresa),
                              ("Datos de ejemplo", self.cargar_datos_ejemplo)):
            ttk.Button(encabezado, text=texto, style="Encabezado.TButton",
                       command=accion).pack(side="right", padx=6)

        # Pestañas
        self.pestanias = ttk.Notebook(raiz)
        self.pestanias.pack(fill="both", expand=True, padx=12, pady=(10, 0))
        self._pestania_registro()
        self._pestania_inspeccion()
        self._pestania_lotes()
        self._pestania_reportes()

        # Barra de estado
        self.estado = tk.StringVar()
        tk.Label(raiz, textvariable=self.estado, bg=AZUL_CLARO, fg=AZUL, anchor="w",
                 font=("Segoe UI", 10), padx=12, pady=6).pack(fill="x", side="bottom")

        self.refrescar()

    # ============================================================
    #  ESTILOS
    # ============================================================

    def _estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10), background=FONDO)
        estilo.configure("TNotebook", background=FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 10, "bold"))
        estilo.map("TNotebook.Tab", background=[("selected", "white")],
                   foreground=[("selected", AZUL)])
        estilo.configure("TFrame", background="white")
        estilo.configure("TLabelframe", background="white", padding=10)
        estilo.configure("TLabelframe.Label", background="white", foreground=AZUL,
                         font=("Segoe UI", 11, "bold"))
        estilo.configure("TLabel", background="white")
        estilo.configure("TCheckbutton", background="white")
        estilo.configure("TButton", padding=(10, 5))
        estilo.configure("Accion.TButton", background=AZUL, foreground="white",
                         font=("Segoe UI", 10, "bold"))
        estilo.map("Accion.TButton", background=[("active", "#2d5486")])
        estilo.configure("Encabezado.TButton", background="#2d5486", foreground="white")
        estilo.map("Encabezado.TButton", background=[("active", "#3c6aa5")])
        estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background=AZUL_CLARO, foreground=AZUL)
        estilo.configure("Resultado.TLabel", font=("Segoe UI", 13, "bold"))

    def _campo(self, padre, fila, texto, widget):
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", pady=3, padx=(0, 8))
        widget.grid(row=fila, column=1, sticky="ew", pady=3)
        return widget

    def _ejecutar(self, accion, mensaje_ok=None):
        """Ejecuta una acción del sistema: si lanza una excepción propia, la muestra."""
        try:
            resultado = accion()
        except CalidadError as e:
            messagebox.showerror(type(e).__name__, str(e))
            return None
        self.refrescar()
        if mensaje_ok:
            self.estado.set(f"✔ {mensaje_ok}")
        return resultado

    # ============================================================
    #  PESTAÑA 1: REGISTRO
    # ============================================================

    def _pestania_registro(self):
        marco = ttk.Frame(self.pestanias, padding=14)
        self.pestanias.add(marco, text="  Registro  ")
        marco.columnconfigure((0, 1, 2), weight=1, uniform="col")

        # Lote
        f = ttk.LabelFrame(marco, text="Nuevo lote")
        f.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.lote_nombre = self._campo(f, 0, "Componentes", ttk.Entry(f))
        self.lote_cantidad = self._campo(f, 1, "Cantidad fabricada", ttk.Entry(f))
        ttk.Button(f, text="Crear lote", style="Accion.TButton",
                   command=self.crear_lote).grid(row=2, column=1, sticky="e", pady=(8, 0))

        # Muestras
        f = ttk.LabelFrame(marco, text="Muestras de un lote")
        f.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.muestra_lote = Selector(f, 22)
        self._campo(f, 0, "Lote", self.muestra_lote.combo)
        self.muestra_cantidad = self._campo(f, 1, "Cant. de muestras", ttk.Entry(f))
        self.muestra_unidades = self._campo(f, 2, "Unidades c/u", ttk.Entry(f))
        ttk.Button(f, text="Crear muestras", style="Accion.TButton",
                   command=self.crear_muestras).grid(row=3, column=1, sticky="e", pady=(8, 0))

        # Profesional
        f = ttk.LabelFrame(marco, text="Nuevo profesional")
        f.grid(row=0, column=2, sticky="nsew", padx=6, pady=6)
        self.prof_nombre = self._campo(f, 0, "Nombre", ttk.Entry(f))
        ttk.Button(f, text="Registrar profesional", style="Accion.TButton",
                   command=self.registrar_profesional).grid(row=1, column=1, sticky="e", pady=(8, 0))

        # Certificación
        f = ttk.LabelFrame(marco, text="Certificación de un profesional")
        f.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.cert_prof = Selector(f, 22)
        self._campo(f, 0, "Profesional", self.cert_prof.combo)
        self.cert_nombre = self._campo(f, 1, "Certificación", ttk.Entry(f))
        self.cert_inicio = self._campo(f, 2, "Desde", ttk.Entry(f))
        self.cert_fin = self._campo(f, 3, "Hasta", ttk.Entry(f))
        self.cert_inicio.insert(0, date.today().isoformat())
        self.cert_fin.insert(0, (date.today() + timedelta(days=365)).isoformat())
        ttk.Button(f, text="Agregar certificación", style="Accion.TButton",
                   command=self.agregar_certificacion).grid(row=4, column=1, sticky="e", pady=(8, 0))

        # Equipo
        f = ttk.LabelFrame(marco, text="Nuevo equipo")
        f.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        self.equipo_categoria = ttk.Combobox(f, state="readonly", values=["Visual", "Dimensional"])
        self.equipo_categoria.set("Visual")
        self._campo(f, 0, "Categoría", self.equipo_categoria)
        self.equipo_fecha = self._campo(f, 1, "Calibración", ttk.Entry(f))
        self.equipo_fecha.insert(0, date.today().isoformat())
        ttk.Label(f, text="Formato AAAA-MM-DD · vale 182 días", foreground="#6b7a90").grid(
            row=2, column=0, columnspan=2, sticky="e")
        ttk.Button(f, text="Registrar equipo", style="Accion.TButton",
                   command=self.registrar_equipo).grid(row=3, column=1, sticky="e", pady=(8, 0))

        # Procedimiento
        f = ttk.LabelFrame(marco, text="Nuevo procedimiento")
        f.grid(row=1, column=2, sticky="nsew", padx=6, pady=6)
        self.proc_tipo = ttk.Combobox(f, state="readonly", values=["Visual", "Dimensional"])
        self.proc_tipo.set("Visual")
        self._campo(f, 0, "Tipo", self.proc_tipo)
        self.proc_limite = self._campo(f, 1, "Límite gravedad", ttk.Entry(f))
        self.proc_cert = self._campo(f, 2, "Certificación", ttk.Entry(f))
        ttk.Button(f, text="Crear procedimiento", style="Accion.TButton",
                   command=self.crear_procedimiento).grid(row=3, column=1, sticky="e", pady=(8, 0))

        for hijo in marco.winfo_children():
            hijo.columnconfigure(1, weight=1)

    def crear_lote(self):
        def accion():
            cantidad = leer_entero(self.lote_cantidad.get(), "cantidad fabricada")
            return self.empresa.crear_registrar_lote(self.lote_nombre.get(), cantidad)
        lote = self._ejecutar(accion)
        if lote:
            self.estado.set(f"✔ Lote '{lote.nombre_componentes}' creado")

    def crear_muestras(self):
        def accion():
            lote = self.muestra_lote.elegido("lote")
            cantidad = leer_entero(self.muestra_cantidad.get(), "cantidad de muestras")
            unidades = leer_entero(self.muestra_unidades.get(), "unidades por muestra")
            for _ in range(cantidad):
                self.empresa.crear_registrar_muestra(unidades, lote)  # el lote controla la capacidad
            return cantidad
        cantidad = self._ejecutar(accion)
        if cantidad:
            self.estado.set(f"✔ Se crearon {cantidad} muestras")

    def registrar_profesional(self):
        self._ejecutar(lambda: self.empresa.crear_registrar_profesional(self.prof_nombre.get()),
                       f"Profesional '{self.prof_nombre.get()}' registrado")

    def agregar_certificacion(self):
        def accion():
            prof = self.cert_prof.elegido("profesional")
            cert = Certificacion(self.cert_nombre.get(), leer_fecha(self.cert_inicio.get()),
                                 leer_fecha(self.cert_fin.get()))
            prof.agregar_certificacion(cert)
        self._ejecutar(accion, "Certificación agregada")

    def registrar_equipo(self):
        self._ejecutar(lambda: self.empresa.crear_registrar_equipo(
            self.equipo_categoria.get(), leer_fecha(self.equipo_fecha.get())), "Equipo registrado")

    def crear_procedimiento(self):
        def accion():
            tipo = ProcedimientoVisual if self.proc_tipo.get() == "Visual" else ProcedimientoDimensional
            datos = {"limite_gravedad_acumulada": leer_entero(self.proc_limite.get(), "límite")}
            if self.proc_cert.get().strip():
                datos["certificacion_requerida"] = self.proc_cert.get().strip()
            return self.empresa.crear_registrar_procedimiento(tipo, **datos)  # **kwargs
        self._ejecutar(accion, "Procedimiento creado")

    # ============================================================
    #  PESTAÑA 2: INSPECCIÓN
    # ============================================================

    def _pestania_inspeccion(self):
        marco = ttk.Frame(self.pestanias, padding=14)
        self.pestanias.add(marco, text="  Inspección  ")
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=2)
        marco.rowconfigure(0, weight=1)

        # Columna izquierda: datos de la inspección
        f = ttk.LabelFrame(marco, text="1. Datos de la inspección")
        f.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        f.columnconfigure(1, weight=1)
        self.insp_lote = Selector(f, 32)
        self._campo(f, 0, "Lote", self.insp_lote.combo)
        self.insp_lote.combo.bind("<<ComboboxSelected>>", lambda e: self.refrescar())
        self.insp_muestra = Selector(f, 32)
        self._campo(f, 1, "Muestra", self.insp_muestra.combo)
        ttk.Button(f, text="Tomar la siguiente de la cola",
                   command=self.siguiente_de_la_cola).grid(row=2, column=1, sticky="w", pady=(0, 8))
        self.insp_prof = Selector(f, 32)
        self._campo(f, 3, "Profesional", self.insp_prof.combo)
        self.insp_equipo = Selector(f, 32)
        self._campo(f, 4, "Equipo", self.insp_equipo.combo)
        self.insp_proc = Selector(f, 32)
        self._campo(f, 5, "Procedimiento", self.insp_proc.combo)
        self.insp_proc.combo.bind("<<ComboboxSelected>>", lambda e: self.cambiar_tipo_observacion())
        self.insp_fecha = self._campo(f, 6, "Fecha (AAAA-MM-DD)", ttk.Entry(f))
        self.insp_fecha.insert(0, date.today().isoformat())

        ttk.Button(f, text="▶  Inspeccionar muestra", style="Accion.TButton",
                   command=self.inspeccionar).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 6))
        self.resultado = ttk.Label(f, text="", style="Resultado.TLabel", wraplength=330)
        self.resultado.grid(row=8, column=0, columnspan=2, sticky="w")
        self.resultado_detalle = ttk.Label(f, text="", wraplength=330, foreground="#4a5568")
        self.resultado_detalle.grid(row=9, column=0, columnspan=2, sticky="w")

        # Columna derecha: observaciones
        f = ttk.LabelFrame(marco, text="2. Observaciones")
        f.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        self.form_obs = ttk.Frame(f)
        self.form_obs.grid(row=0, column=0, sticky="ew")
        self.obs_desc = tk.StringVar()
        self.obs_detectado = tk.BooleanVar(value=True)
        self.obs_gravedad = tk.StringVar(value="1")
        self.obs_valor = tk.StringVar()
        self.obs_min = tk.StringVar()
        self.obs_max = tk.StringVar()
        self.tipo_obs = None

        botones = ttk.Frame(f)
        botones.grid(row=1, column=0, sticky="w", pady=6)
        ttk.Button(botones, text="+ Agregar observación", command=self.agregar_observacion).pack(side="left")
        ttk.Button(botones, text="Vaciar lista", command=self.vaciar_observaciones).pack(side="left", padx=6)

        self.tabla_obs = ttk.Treeview(f, columns=("desc", "detalle"), show="headings", height=8)
        self.tabla_obs.heading("desc", text="Descripción")
        self.tabla_obs.heading("detalle", text="Detalle")
        self.tabla_obs.column("desc", width=260)
        self.tabla_obs.column("detalle", width=320)
        self.tabla_obs.grid(row=2, column=0, sticky="nsew")
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
        ttk.Label(self.form_obs, text="Descripción").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.form_obs, textvariable=self.obs_desc, width=40).grid(row=0, column=1, columnspan=5, sticky="w", pady=3)
        if tipo == "visual":
            ttk.Checkbutton(self.form_obs, text="Se detectó un defecto",
                            variable=self.obs_detectado).grid(row=1, column=1, sticky="w")
            ttk.Label(self.form_obs, text="Gravedad (1 a 5)").grid(row=1, column=2, padx=(16, 4))
            ttk.Spinbox(self.form_obs, from_=1, to=5, width=4,
                        textvariable=self.obs_gravedad).grid(row=1, column=3, sticky="w")
        else:
            for col, (texto, var) in enumerate((("Valor medido", self.obs_valor),
                                                ("Tol. mínima", self.obs_min),
                                                ("Tol. máxima", self.obs_max))):
                ttk.Label(self.form_obs, text=texto).grid(row=1, column=col * 2, sticky="w", padx=(0, 4))
                ttk.Entry(self.form_obs, textvariable=var, width=8).grid(row=1, column=col * 2 + 1, sticky="w", padx=(0, 12))

    def agregar_observacion(self):
        try:
            if self.tipo_obs == "visual":
                detectado = self.obs_detectado.get()
                gravedad = leer_entero(self.obs_gravedad.get(), "gravedad") if detectado else None
                obs = ObservacionVisual(self.obs_desc.get(), detectado, gravedad)
                detalle = f"Defecto de gravedad {gravedad}" if detectado else "Sin defecto"
            else:
                obs = ObservacionDimensional(leer_decimal(self.obs_valor.get(), "valor medido"),
                                             leer_decimal(self.obs_min.get(), "tolerancia mínima"),
                                             leer_decimal(self.obs_max.get(), "tolerancia máxima"),
                                             self.obs_desc.get())
                fuera = "FUERA de tolerancia" if obs.desviacion > 0 else "dentro de tolerancia"
                detalle = f"{obs.valor_medido} en [{obs.tolerancia_min}, {obs.tolerancia_max}] → {fuera}"
        except CalidadError as e:
            messagebox.showerror(type(e).__name__, str(e))
            return
        self.observaciones.append(obs)
        self.tabla_obs.insert("", "end", values=(obs.descripcion, detalle))
        self.obs_desc.set("")

    def vaciar_observaciones(self):
        self.observaciones = []
        self.tabla_obs.delete(*self.tabla_obs.get_children())

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
        color = "#1e7b34" if muestra.estado == EstadoMuestra.CONFORME else "#b42318"
        self.resultado.configure(text=f"Muestra {estado}", foreground=color)
        detalle = (f"{len(defectos)} defecto(s) · suma de gravedades {muestra.suma_gravedades()} "
                   f"(límite {proc.limite_gravedad_acumulada}) · "
                   f"{'con' if muestra.tiene_critico() else 'sin'} defecto crítico")
        if muestra.reporte is not None:
            detalle += "\nSe generó un reporte de desviación (pestaña Reportes)."
        self.resultado_detalle.configure(text=detalle)
        self.vaciar_observaciones()
        self.siguiente_de_la_cola(avisar=False)  # deja elegida la próxima pendiente
        self.estado.set(f"✔ Inspección cerrada: muestra {estado}")

    # ============================================================
    #  PESTAÑA 3: LOTES
    # ============================================================

    def _pestania_lotes(self):
        marco = ttk.Frame(self.pestanias, padding=14)
        self.pestanias.add(marco, text="  Lotes y muestras  ")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(1, weight=1)
        marco.rowconfigure(3, weight=2)

        barra = ttk.Frame(marco)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(barra, text="Lotes", font=("Segoe UI", 12, "bold"), foreground=AZUL).pack(side="left")
        ttk.Button(barra, text="Decidir lote seleccionado", style="Accion.TButton",
                   command=self.decidir_lote).pack(side="right")

        columnas = ("nombre", "estado", "fabricada", "muestras", "pendientes", "no_conf", "criticos")
        titulos = ("Componentes", "Estado", "Fabricada", "Muestras", "Pendientes", "% no conforme", "Críticos")
        self.tabla_lotes = self._tabla(marco, columnas, titulos, 6)
        self._con_scroll(marco, self.tabla_lotes, 1)
        self.tabla_lotes.bind("<<TreeviewSelect>>", lambda e: self.mostrar_muestras())

        ttk.Label(marco, text="Muestras del lote seleccionado", font=("Segoe UI", 12, "bold"),
                  foreground=AZUL).grid(row=2, column=0, sticky="w", pady=(14, 6))
        columnas = ("id", "cantidad", "estado", "defectos", "suma", "historial")
        titulos = ("Muestra", "Unidades", "Estado", "Defectos", "Suma gravedades", "Historial (pila)")
        self.tabla_muestras = self._tabla(marco, columnas, titulos, 10)
        self.tabla_muestras.column("historial", width=380)
        self._con_scroll(marco, self.tabla_muestras, 3)

    def _tabla(self, padre, columnas, titulos, alto):
        tabla = ttk.Treeview(padre, columns=columnas, show="headings", height=alto)
        for col, titulo in zip(columnas, titulos):
            tabla.heading(col, text=titulo)
            tabla.column(col, width=120, anchor="center")
        for estado, color in COLORES_ESTADO.items():
            tabla.tag_configure(estado, background=color)
        return tabla

    def _con_scroll(self, padre, tabla, fila):
        """Ubica la tabla con una barra de desplazamiento vertical a la derecha."""
        contenedor = ttk.Frame(padre)
        contenedor.grid(row=fila, column=0, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(0, weight=1)
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.grid(in_=contenedor, row=0, column=0, sticky="nsew")
        tabla.lift(contenedor)  # la tabla se creó antes que el contenedor: la traemos al frente
        barra.grid(row=0, column=1, sticky="ns")

    def mostrar_muestras(self):
        self.tabla_muestras.delete(*self.tabla_muestras.get_children())
        seleccion = self.tabla_lotes.selection()
        if not seleccion:
            return
        lote = self._lotes_por_fila.get(seleccion[0])
        for m in lote.muestras:
            historial = " → ".join(map(lambda e: e.value, m.historial_estados))
            self.tabla_muestras.insert("", "end", tags=(m.estado.value,), values=(
                id_corto(m.id), m.cantidad, m.estado.value, len(m.defectos),
                m.suma_gravedades(), historial))

    def decidir_lote(self):
        seleccion = self.tabla_lotes.selection()
        if not seleccion:
            messagebox.showinfo("Decidir lote", "Seleccioná un lote de la tabla")
            return
        lote = self._lotes_por_fila[seleccion[0]]
        estado = self._ejecutar(lote.decidir)
        if estado:
            messagebox.showinfo("Decisión del lote",
                                f"Lote {estado.value}\n\n{lote.porcentaje_no_conforme():.1f}% de muestras "
                                f"no conformes (se rechaza si supera el 5%)")
            self.estado.set(f"✔ Lote '{lote.nombre_componentes}' {estado.value}")

    # ============================================================
    #  PESTAÑA 4: REPORTES
    # ============================================================

    def _pestania_reportes(self):
        marco = ttk.Frame(self.pestanias, padding=14)
        self.pestanias.add(marco, text="  Reportes  ")
        marco.columnconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(1, weight=1)

        barra = ttk.Frame(marco)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(barra, text="Reportes de desviación (muestras no conformes)",
                  font=("Segoe UI", 12, "bold"), foreground=AZUL).pack(side="left")
        ttk.Button(barra, text="Exportar a JSON", command=self.exportar_json).pack(side="right")

        self.tabla_reportes = self._tabla(marco, ("id", "muestra", "fecha", "defectos"),
                                          ("Reporte", "Muestra", "Fecha", "Defectos"), 12)
        self.tabla_reportes.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        self.tabla_reportes.bind("<<TreeviewSelect>>", lambda e: self.mostrar_reporte())

        self.detalle_reporte = tk.Text(marco, wrap="word", font=("Consolas", 10), relief="flat",
                                       background=AZUL_CLARO, padx=10, pady=10)
        self.detalle_reporte.grid(row=1, column=1, sticky="nsew")

    def mostrar_reporte(self):
        seleccion = self.tabla_reportes.selection()
        if not seleccion:
            return
        r = self._reportes_por_fila[seleccion[0]]
        historial = " → ".join(map(lambda e: e.value, r.historial_estados))
        texto = (f"Reporte:      {r.id}\nMuestra:      {r.muestra_id}\nLote:         {r.lote_id}\n"
                 f"Profesional:  {r.profesional_id}\nFecha:        {r.fecha}\n"
                 f"Historial:    {historial}\n\nDefectos ({len(r.defectos)}):\n")
        texto += "\n".join(map(lambda d: f"  • [{d.tipo}] {d.descripcion} — gravedad {d.gravedad}"
                                         f"{' (CRÍTICO)' if d.es_critico() else ''}", r.defectos))
        self.detalle_reporte.delete("1.0", "end")
        self.detalle_reporte.insert("1.0", texto)

    def exportar_json(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".json", initialfile="reportes.json",
                                            filetypes=[("JSON", "*.json")])
        if ruta:
            cantidad = self._ejecutar(lambda: self.empresa.exportar_reportes_json(ruta))
            self.estado.set(f"✔ Se exportaron {cantidad} reporte(s) a {ruta}")

    # ============================================================
    #  GUARDAR / CARGAR / DATOS DE EJEMPLO
    # ============================================================

    def guardar_empresa(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".pkl", initialfile="empresa.pkl",
                                            filetypes=[("Pickle", "*.pkl")])
        if ruta:
            self._ejecutar(lambda: self.empresa.guardar(ruta), f"Empresa guardada en {ruta}")

    def cargar_empresa(self):
        ruta = filedialog.askopenfilename(filetypes=[("Pickle", "*.pkl"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            self.empresa = Empresa.cargar(ruta)
        except CalidadError as e:
            messagebox.showerror(type(e).__name__, str(e))
            return
        self.refrescar()
        self.estado.set(f"✔ Empresa cargada desde {ruta}")

    def cargar_datos_ejemplo(self):
        hoy = date.today()
        lote = self.empresa.crear_registrar_lote("Tornillos M8", 200)
        for _ in range(20):
            self.empresa.crear_registrar_muestra(10, lote)
        ana = self.empresa.crear_registrar_profesional("Ana")
        ana.agregar_certificacion(Certificacion("ISO", hoy - timedelta(days=30), hoy + timedelta(days=335)))
        self.empresa.crear_registrar_profesional("Carlos")  # sin certificaciones
        self.empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=30))
        self.empresa.crear_registrar_equipo("Dimensional", hoy - timedelta(days=60))
        self.empresa.crear_registrar_equipo("Visual", hoy - timedelta(days=200))  # vencido
        self.empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5,
                                                   certificacion_requerida="ISO")
        self.empresa.crear_registrar_procedimiento(ProcedimientoDimensional, limite_gravedad_acumulada=10)
        self.refrescar()
        messagebox.showinfo("Datos de ejemplo",
                            "Se cargaron:\n\n• Lote de 200 tornillos con 20 muestras\n"
                            "• Ana (certificación ISO vigente) y Carlos (sin certificaciones)\n"
                            "• Equipo visual, equipo dimensional y un equipo visual VENCIDO (200 días)\n"
                            "• Procedimiento visual (límite 5, pide ISO) y dimensional (límite 10)")

    # ============================================================
    #  REFRESCAR TODA LA INTERFAZ
    # ============================================================

    def _describir_muestra(self, m):
        return f"Muestra {id_corto(m.id)} · {m.cantidad} u. · {m.estado.value}"

    def refrescar(self):
        e = self.empresa
        hoy = date.today()
        describir_lote = lambda l: f"{l.nombre_componentes} ({id_corto(l.id)}) · {l.estado.value}"
        describir_prof = lambda p: (f"{p.nombre} · certificaciones: "
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
        seleccion = self.tabla_lotes.selection()
        id_seleccionado = self._lotes_por_fila[seleccion[0]].id if seleccion else None
        self.tabla_lotes.delete(*self.tabla_lotes.get_children())
        self._lotes_por_fila = {}
        for lote in e.listar_lotes():
            fila = self.tabla_lotes.insert("", "end", tags=(lote.estado.value,), values=(
                lote.nombre_componentes, lote.estado.value, lote.cantidad_fabricada,
                len(lote.muestras), len(lote.pendientes_en_orden()),
                f"{lote.porcentaje_no_conforme():.1f}%", lote.total_defectos_criticos()))
            self._lotes_por_fila[fila] = lote
            if lote.id == id_seleccionado:
                self.tabla_lotes.selection_set(fila)
        self.mostrar_muestras()

        # Tabla de reportes
        self.tabla_reportes.delete(*self.tabla_reportes.get_children())
        self._reportes_por_fila = {}
        for r in e.reportes():
            fila = self.tabla_reportes.insert("", "end", values=(
                id_corto(r.id), id_corto(r.muestra_id), r.fecha, len(r.defectos)))
            self._reportes_por_fila[fila] = r

        resumen = e.resumen()
        self.estado.set(f"Lotes: {resumen['lotes']}  ·  Muestras: {resumen['muestras']}  ·  "
                        f"Profesionales: {resumen['profesionales']}  ·  Equipos: {resumen['equipos']}  ·  "
                        f"Inspecciones: {resumen['inspecciones']}  ·  Reportes: {len(e.reportes())}")


if __name__ == "__main__":
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()