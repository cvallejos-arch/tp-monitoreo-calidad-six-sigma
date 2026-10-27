"""Interfaz gráfica del sistema de monitoreo de calidad (QuantumTech Precision)."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.certificacion import Certificacion
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.estado_muestra import EstadoMuestra
from classes.estado_lote import EstadoLote
from classes.simulador import Simulador
from classes.excepciones import CalidadError, DatosInvalidosError, TransicionIlegalError


  
#  PALETA Y TIPOGRAFÍA
  

FUENTE = "Segoe UI"
LATERAL = "#1f4e8c"          # barra lateral
LATERAL_ACTIVO = "#2f66b0"   # opción elegida de la barra lateral
FONDO = "#eef3fb"            # fondo general
BLANCO = "#ffffff"
BORDE = "#dbe4f1"
TEXTO = "#24324a"
SUAVE = "#8a98b0"
AZUL = "#1f4e8c"
CELESTE = "#4fb8d6"
NARANJA = "#f39a5b"
NARANJA_ACTIVO = "#e5833f"
VERDE = "#2e9e6a"
ROJO = "#d6455d"
AMARILLO = "#e0a526"
GRIS = "#a9b5c7"

# Color de cada estado (fuerte para gráficos, suave para el fondo de las tablas)
COLOR_ESTADO = {
    "PENDIENTE": GRIS, "EN_INSPECCION": AMARILLO, "CONFORME": VERDE, "NO_CONFORME": ROJO,
    "EN_PRODUCCION": CELESTE, "APROBADO": VERDE, "RECHAZADO": ROJO,
}
FONDO_ESTADO = {
    "PENDIENTE": "#f1f4f8", "EN_INSPECCION": "#fff4d6", "CONFORME": "#e1f5ea",
    "NO_CONFORME": "#fde4e8", "EN_PRODUCCION": "#e3f3f9", "APROBADO": "#e1f5ea",
    "RECHAZADO": "#fde4e8",
}
# Gravedad 1 (leve) a 5 (crítico): de verde a rojo
COLOR_GRAVEDAD = {1: "#7cc6a4", 2: "#b8d36a", 3: "#f2c14e", 4: "#f39a5b", 5: "#d6455d"}

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")


  
#  FUNCIONES AUXILIARES (lectura de datos y textos)
  

def id_corto(obj_id):
    return str(obj_id)[:8]


def fecha_larga(fecha):
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


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


def texto_historial(historial):
    return " → ".join(map(lambda e: e.value, historial))


def promedio(valores):
    """Promedio de una lista de números (0 si está vacía)."""
    valores = list(valores)
    return sum(valores) / len(valores) if valores else 0


  
#  COMPONENTES VISUALES
  

class Selector:
    """Combobox que muestra textos pero devuelve el objeto elegido."""

    def __init__(self, padre, ancho=40):
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


def boton(padre, texto, comando, tipo="primario"):
    """Botón plano con los colores de la app (primario naranja, secundario celeste)."""
    colores = {
        "primario": (NARANJA, BLANCO, NARANJA_ACTIVO),
        "secundario": ("#e6eefa", AZUL, "#d4e2f6"),
        "oscuro": (AZUL, BLANCO, LATERAL_ACTIVO),
    }
    fondo, letra, activo = colores[tipo]
    return tk.Button(padre, text=texto, command=comando, bg=fondo, fg=letra,
                     activebackground=activo, activeforeground=letra, relief="flat", bd=0,
                     cursor="hand2", padx=14, pady=6, font=(FUENTE, 10, "bold"))


def tarjeta(padre, titulo=None, subtitulo=None):
    """Tarjeta blanca con borde suave. Devuelve (marco exterior, cuerpo)."""
    marco = tk.Frame(padre, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
    if titulo:
        cabecera = tk.Frame(marco, bg=BLANCO)
        cabecera.pack(fill="x", padx=16, pady=(10, 0))
        tk.Label(cabecera, text=titulo, bg=BLANCO, fg=TEXTO,
                 font=(FUENTE, 12, "bold")).pack(anchor="w")
        if subtitulo:
            tk.Label(cabecera, text=subtitulo, bg=BLANCO, fg=SUAVE,
                     font=(FUENTE, 8)).pack(anchor="w")
    cuerpo = tk.Frame(marco, bg=BLANCO)
    cuerpo.pack(fill="both", expand=True, padx=16, pady=(6, 10))
    return marco, cuerpo


def rectangulo_redondeado(c, x1, y1, x2, y2, radio, **opciones):
    """Rectángulo con esquinas redondeadas en un Canvas (polígono suavizado)."""
    radio = min(radio, (x2 - x1) / 2, (y2 - y1) / 2)
    puntos = (x1 + radio, y1, x2 - radio, y1, x2, y1, x2, y1 + radio, x2, y2 - radio, x2, y2,
              x2 - radio, y2, x1 + radio, y2, x1, y2, x1, y2 - radio, x1, y1 + radio, x1, y1)
    return c.create_polygon(puntos, smooth=True, **opciones)


class Grafico(tk.Canvas):
    """Canvas que se redibuja solo cuando cambia de tamaño.
    Se le pasa una función dibujar(canvas, ancho, alto)."""

    def __init__(self, padre, alto=200):
        super().__init__(padre, height=alto, bg=BLANCO, highlightthickness=0)
        self._dibujo = None
        self.bind("<Configure>", lambda e: self._redibujar())

    def mostrar(self, dibujo):
        self._dibujo = dibujo
        self._redibujar()

    def _redibujar(self):
        self.delete("all")
        if self._dibujo is not None:
            self._dibujo(self, self.winfo_width(), self.winfo_height())


# --- Funciones que devuelven "dibujos" para un Grafico ---

def sin_datos(texto="Sin datos todavía · probá con «Datos de ejemplo»"):
    def dibujar(c, w, h):
        c.create_text(w / 2, h / 2, text=texto, fill=SUAVE, font=(FUENTE, 10))
    return dibujar


def dona(partes, texto_centro, sub_centro):
    """Gráfico de dona. partes = [(etiqueta, valor, color)]."""
    total = sum(map(lambda p: p[1], partes))
    if total == 0:
        return sin_datos()

    def dibujar(c, w, h):
        d = min(h - 16, w * 0.36)
        x0, y0 = 8, (h - d) / 2
        inicio = 90
        for _, valor, color in partes:
            if valor == 0:
                continue
            extension = -360 * valor / total
            if valor == total:  # un solo sector: create_arc no dibuja 360°
                c.create_oval(x0, y0, x0 + d, y0 + d, fill=color, outline=BLANCO)
            else:
                c.create_arc(x0, y0, x0 + d, y0 + d, start=inicio, extent=extension,
                             fill=color, outline=BLANCO, width=2)
            inicio += extension
        cx, cy, hueco = x0 + d / 2, y0 + d / 2, d * 0.31
        c.create_oval(cx - hueco, cy - hueco, cx + hueco, cy + hueco, fill=BLANCO, outline=BLANCO)
        c.create_text(cx, cy - 7, text=texto_centro, fill=TEXTO, font=(FUENTE, 15, "bold"))
        c.create_text(cx, cy + 13, text=sub_centro, fill=SUAVE, font=(FUENTE, 8))
        # Leyenda
        x = x0 + d + 18
        alto_fila = min(26, (h - 10) / max(len(partes), 1))
        y = h / 2 - alto_fila * len(partes) / 2 + alto_fila / 2
        for etiqueta, valor, color in partes:
            rectangulo_redondeado(c, x, y - 6, x + 12, y + 6, 4, fill=color, outline=color)
            c.create_text(x + 18, y, text=etiqueta, anchor="w", fill=TEXTO, font=(FUENTE, 8))
            c.create_text(w - 4, y, text=f"{valor} · {valor / total:.0%}", anchor="e",
                          fill=SUAVE, font=(FUENTE, 8, "bold"))
            y += alto_fila
    return dibujar


def barras_verticales(datos, texto_valor=str):
    """Barras verticales. datos = [(etiqueta, valor, color)]."""
    if not any(map(lambda d: d[1], datos)):
        return sin_datos()

    def dibujar(c, w, h):
        maximo = max(map(lambda d: d[1], datos)) or 1
        arriba, abajo = 22, 26
        espacio = (w - 10) / len(datos)
        ancho = min(44, espacio * 0.55)
        c.create_line(5, h - abajo, w - 5, h - abajo, fill=BORDE)
        for i, (etiqueta, valor, color) in enumerate(datos):
            cx = 5 + espacio * i + espacio / 2
            alto = (h - arriba - abajo) * valor / maximo
            if valor > 0:
                rectangulo_redondeado(c, cx - ancho / 2, h - abajo - alto, cx + ancho / 2,
                                      h - abajo, 6, fill=color, outline=color)
            c.create_text(cx, h - abajo - alto - 9, text=texto_valor(valor), fill=TEXTO,
                          font=(FUENTE, 9, "bold"))
            c.create_text(cx, h - abajo + 13, text=etiqueta, fill=SUAVE, font=(FUENTE, 9))
    return dibujar


def barras_horizontales(datos, maximo=None, umbral=None, texto_umbral="", max_filas=7,
                        margen_derecho=62):
    """Barras horizontales. datos = [(etiqueta, valor, color, texto_derecha)].
    umbral: dibuja una línea punteada vertical (por ejemplo, el 5 % del lote)."""
    if not datos:
        return sin_datos()

    def dibujar(c, w, h):
        filas = datos[:max_filas]
        tope = maximo if maximo is not None else max(map(lambda d: d[1], filas)) or 1
        if umbral is not None:
            tope = max(tope, umbral * 1.6)
        x_inicio, x_fin = 100, w - margen_derecho
        arriba = 18 if umbral is not None else 4
        alto_fila = min(30, (h - arriba - (14 if len(datos) > max_filas else 0)) / len(filas))
        for i, (etiqueta, valor, color, texto) in enumerate(filas):
            y = arriba + alto_fila * i + alto_fila / 2
            c.create_text(x_inicio - 10, y, text=etiqueta[:14], anchor="e", fill=TEXTO, font=(FUENTE, 9))
            rectangulo_redondeado(c, x_inicio, y - 7, x_fin, y + 7, 7, fill="#f0f4fa", outline="#f0f4fa")
            largo = (x_fin - x_inicio) * min(valor / tope, 1)
            if largo > 2:
                rectangulo_redondeado(c, x_inicio, y - 7, x_inicio + largo, y + 7, 7,
                                      fill=color, outline=color)
            c.create_text(x_fin + 8, y, text=texto, anchor="w", fill=TEXTO, font=(FUENTE, 9, "bold"))
        if umbral is not None:
            xu = x_inicio + (x_fin - x_inicio) * umbral / tope
            c.create_line(xu, arriba - 4, xu, arriba + alto_fila * len(filas), fill=ROJO, dash=(4, 3))
            c.create_text(xu, 8, text=texto_umbral, fill=ROJO, font=(FUENTE, 8, "bold"))
        if len(datos) > max_filas:
            c.create_text(w / 2, h - 6, text=f"y {len(datos) - max_filas} más…", fill=SUAVE,
                          font=(FUENTE, 8))
    return dibujar


def contadores(datos):
    """Fila de contadores: un número grande de color y su etiqueta debajo.
    datos = [(etiqueta, valor, color)]."""
    def dibujar(c, w, h):
        espacio = w / len(datos)
        for i, (etiqueta, valor, color) in enumerate(datos):
            cx = espacio * i + espacio / 2
            c.create_text(cx, h / 2 - 9, text=str(valor), fill=color, font=(FUENTE, 16, "bold"))
            c.create_text(cx, h / 2 + 13, text=etiqueta, fill=SUAVE, font=(FUENTE, 9))
            if i > 0:
                c.create_line(espacio * i, 6, espacio * i, h - 6, fill="#eef2f8")
    return dibujar


def lista_con_insignias(filas):
    """Lista de filas con una insignia de color a la derecha.
    filas = [(titulo, detalle, texto_insignia, color)]."""
    if not filas:
        return sin_datos()

    def dibujar(c, w, h):
        alto_fila = min(40, h / len(filas))
        for i, (titulo, detalle, insignia, color) in enumerate(filas):
            y = alto_fila * i + alto_fila / 2
            c.create_oval(4, y - 4, 12, y + 4, fill=color, outline=color)
            ancho = 16 + len(insignia) * 7
            maximo = max(8, int((w - ancho - 34) / 7))
            if len(titulo) > maximo:
                titulo = titulo[:maximo - 1] + "…"
            c.create_text(22, y - 7, text=titulo, anchor="w", fill=TEXTO, font=(FUENTE, 9, "bold"))
            c.create_text(22, y + 8, text=detalle, anchor="w", fill=SUAVE, font=(FUENTE, 8))
            ancho = 16 + len(insignia) * 7
            rectangulo_redondeado(c, w - ancho - 4, y - 10, w - 4, y + 10, 10,
                                  fill=FONDO_ESTADO.get(insignia, "#eef3fb"), outline="")
            c.create_text(w - 4 - ancho / 2, y, text=insignia, fill=color, font=(FUENTE, 8, "bold"))
            if i < len(filas) - 1:
                c.create_line(22, y + alto_fila / 2, w - 4, y + alto_fila / 2, fill="#eef2f8")
    return dibujar


def barras_de_progreso(filas):
    """Filas con una barra de progreso. filas = [(etiqueta, fraccion, color, texto_derecha)].
    desde_y permite dibujarlas debajo de otro contenido del mismo canvas."""
    if not filas:
        return sin_datos()

    def dibujar(c, w, h, desde_y=0):
        alto_fila = min(40, (h - desde_y) / len(filas))
        for i, (etiqueta, fraccion, color, texto) in enumerate(filas):
            y = desde_y + alto_fila * i + alto_fila / 2
            c.create_text(0, y - 8, text=etiqueta, anchor="w", fill=TEXTO, font=(FUENTE, 9))
            c.create_text(w, y - 8, text=texto, anchor="e", fill=color, font=(FUENTE, 9, "bold"))
            rectangulo_redondeado(c, 0, y + 3, w, y + 11, 4, fill="#eef2f8", outline="")
            if fraccion > 0:
                rectangulo_redondeado(c, 0, y + 3, max(8, w * min(fraccion, 1)), y + 11, 4,
                                      fill=color, outline="")
    return dibujar


  
#  APLICACIÓN
  

class App:
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
        self._estilos()

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
            pagina = tk.Frame(contenedor, bg=FONDO)
            pagina.grid(row=0, column=0, sticky="nsew")
            self.paginas[clave] = pagina
        self._pagina_panel(self.paginas["panel"])
        self._pagina_registro(self.paginas["registro"])
        self._pagina_inspeccion(self.paginas["inspeccion"])
        self._pagina_lotes(self.paginas["lotes"])
        self._pagina_reportes(self.paginas["reportes"])

        # Barra de estado
        self.estado = tk.StringVar()
        tk.Label(principal, textvariable=self.estado, bg=FONDO, fg=AZUL, anchor="w",
                 font=(FUENTE, 9), padx=28, pady=8).grid(row=2, column=0, sticky="ew")

        self.mostrar_pagina("panel")
        self.refrescar()

      
    #  ESTILOS Y ESTRUCTURA
      

    def _estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(".", font=(FUENTE, 10), background=BLANCO)
        estilo.configure("TEntry", fieldbackground="#f6f9fd", bordercolor=BORDE,
                         lightcolor=BORDE, darkcolor=BORDE, padding=5)
        estilo.configure("TCombobox", fieldbackground="#f6f9fd", background="#f6f9fd",
                         bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE, padding=4,
                         arrowcolor=AZUL)
        estilo.map("TCombobox", fieldbackground=[("readonly", "#f6f9fd")])
        estilo.configure("TSpinbox", fieldbackground="#f6f9fd", bordercolor=BORDE,
                         arrowcolor=AZUL, padding=3)
        estilo.configure("TCheckbutton", background=BLANCO, foreground=TEXTO)
        estilo.configure("Treeview", rowheight=28, font=(FUENTE, 10), background=BLANCO,
                         fieldbackground=BLANCO, bordercolor=BORDE, foreground=TEXTO)
        estilo.configure("Treeview.Heading", font=(FUENTE, 9, "bold"), background="#f3f7fc",
                         foreground=SUAVE, relief="flat", padding=6)
        estilo.map("Treeview", background=[("selected", "#cfe0f6")],
                   foreground=[("selected", TEXTO)])
        estilo.configure("Vertical.TScrollbar", background="#e6eefa", troughcolor=BLANCO,
                         bordercolor=BLANCO, arrowcolor=AZUL)

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

      
    #  PÁGINA 1: PANEL DE CONTROL
      

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
            (2, 1, "equipos", "Calibración de equipos", "validez de 182 días", 140),
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
        filas_equipos = []
        for equipo in e.listar_equipos():
            restantes = 182 - (hoy - equipo.fecha_calibracion).days
            if not equipo.esta_calibrado(hoy):
                color, texto = ROJO, "VENCIDO"
            else:
                color, texto = (AMARILLO if restantes <= 30 else VERDE), f"{restantes} días"
            filas_equipos.append((f"{equipo.categoria} · {id_corto(equipo.id)}",
                                  max(restantes, 0) / 182, color, texto))
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

      
    #  PÁGINA 2: REGISTRO
      

    def _pagina_registro(self, pagina):
        pagina.columnconfigure((0, 1, 2), weight=1, uniform="col")

        def nueva(fila, col, titulo, sub):
            marco, cuerpo = tarjeta(pagina, titulo, sub)
            marco.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)
            cuerpo.columnconfigure(1, weight=1)
            return cuerpo

        f = nueva(1, 0, "Nuevo lote", "partida de componentes")
        self.lote_nombre = self._campo(f, 0, "Componentes", ttk.Entry(f))
        self.lote_cantidad = self._campo(f, 1, "Cantidad fabricada", ttk.Entry(f))
        boton(f, "Crear lote", self.crear_lote).grid(row=2, column=1, sticky="e", pady=(10, 0))

        f = nueva(1, 1, "Muestras", "las crea el lote")
        self.muestra_lote = Selector(f, 22)
        self._campo(f, 0, "Lote", self.muestra_lote.combo)
        self.muestra_cantidad = self._campo(f, 1, "Cant. de muestras", ttk.Entry(f))
        self.muestra_unidades = self._campo(f, 2, "Unidades c/u", ttk.Entry(f))
        boton(f, "Crear muestras", self.crear_muestras).grid(row=3, column=1, sticky="e", pady=(10, 0))

        f = nueva(1, 2, "Nuevo profesional", "quien inspecciona")
        self.prof_nombre = self._campo(f, 0, "Nombre", ttk.Entry(f))
        boton(f, "Registrar profesional", self.registrar_profesional).grid(
            row=1, column=1, sticky="e", pady=(10, 0))

        f = nueva(2, 0, "Certificación", "fechas AAAA-MM-DD · bornes inclusivos")
        self.cert_prof = Selector(f, 22)
        self._campo(f, 0, "Profesional", self.cert_prof.combo)
        self.cert_nombre = self._campo(f, 1, "Certificación", ttk.Entry(f))
        self.cert_inicio = self._campo(f, 2, "Desde", ttk.Entry(f))
        self.cert_fin = self._campo(f, 3, "Hasta", ttk.Entry(f))
        self.cert_inicio.insert(0, date.today().isoformat())
        self.cert_fin.insert(0, (date.today() + timedelta(days=365)).isoformat())
        boton(f, "Agregar certificación", self.agregar_certificacion).grid(
            row=4, column=1, sticky="e", pady=(10, 0))

        f = nueva(2, 1, "Nuevo equipo", "la calibración vale 182 días")
        self.equipo_categoria = ttk.Combobox(f, state="readonly", values=["Visual", "Dimensional"])
        self.equipo_categoria.set("Visual")
        self._campo(f, 0, "Categoría", self.equipo_categoria)
        self.equipo_fecha = self._campo(f, 1, "Calibración", ttk.Entry(f))
        self.equipo_fecha.insert(0, date.today().isoformat())
        boton(f, "Registrar equipo", self.registrar_equipo).grid(row=2, column=1, sticky="e", pady=(10, 0))

        f = nueva(2, 2, "Nuevo procedimiento", "visual o dimensional")
        self.proc_tipo = ttk.Combobox(f, state="readonly", values=["Visual", "Dimensional"])
        self.proc_tipo.set("Visual")
        self._campo(f, 0, "Tipo", self.proc_tipo)
        self.proc_limite = self._campo(f, 1, "Límite gravedad", ttk.Entry(f))
        self.proc_cert = self._campo(f, 2, "Certificación", ttk.Entry(f))
        tk.Label(f, text="Certificación opcional",
                 bg=BLANCO, fg=SUAVE, font=(FUENTE, 8)).grid(row=3, column=0, columnspan=2, sticky="w")
        boton(f, "Crear procedimiento", self.crear_procedimiento).grid(
            row=4, column=1, sticky="e", pady=(10, 0))

        # Resumen del registro: una franja de contadores arriba de los formularios
        franja = tk.Frame(pagina, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
        franja.grid(row=0, column=0, columnspan=3, sticky="ew", padx=6, pady=(6, 4))
        self.resumen_registro = Grafico(franja, 52)
        self.resumen_registro.pack(fill="x", padx=10, pady=4)

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
            if cantidad <= 0:
                raise DatosInvalidosError("La cantidad de muestras debe ser mayor a 0")
            # Controlamos ANTES de crear: o se crean todas las muestras o ninguna
            libre = lote.cantidad_fabricada - sum(map(lambda m: m.cantidad, lote.muestras))
            if cantidad * unidades > libre:
                raise TransicionIlegalError(
                    f"No entran {cantidad} muestras de {unidades} unidades "
                    f"({cantidad * unidades} en total): al lote le quedan {libre} unidades libres. "
                    f"No se creó ninguna muestra."
                )
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

      
    #  PÁGINA 3: INSPECCIÓN
      

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

      
    #  PÁGINA 4: LOTES Y MUESTRAS
      

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

      
    #  PÁGINA 5: REPORTES
      

    def _pagina_reportes(self, pagina):
        pagina.columnconfigure((0, 1), weight=1, uniform="reportes")
        pagina.rowconfigure(0, weight=1)

        marco, cuerpo = tarjeta(pagina, "Reportes", "uno por cada muestra no conforme")
        marco.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        cuerpo.columnconfigure(0, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        self.tabla_reportes = self._tabla(cuerpo, ("id", "muestra", "fecha", "defectos", "maxima"),
                                          ("REPORTE", "MUESTRA", "FECHA", "DEFECTOS", "GRAV. MÁX."),
                                          10, fila=0)
        for col in ("id", "muestra", "fecha", "defectos", "maxima"):
            self.tabla_reportes.column(col, width=88)
        self.tabla_reportes.tag_configure("critico", background=FONDO_ESTADO["NO_CONFORME"])
        self.tabla_reportes.bind("<<TreeviewSelect>>", lambda e: self.mostrar_reporte())
        boton(cuerpo, "Exportar a JSON", self.exportar_json).grid(row=1, column=0, sticky="e", pady=(10, 0))

        marco, cuerpo = tarjeta(pagina, "Detalle del reporte")
        marco.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self.detalle_reporte = tk.Text(cuerpo, wrap="word", font=("Consolas", 10), relief="flat",
                                       background="#f6f9fd", foreground=TEXTO, padx=14, pady=12,
                                       highlightthickness=0)
        self.detalle_reporte.pack(fill="both", expand=True)
        self.detalle_reporte.tag_configure("titulo", font=(FUENTE, 12, "bold"), foreground=AZUL)
        self.detalle_reporte.tag_configure("critico", foreground=ROJO, font=("Consolas", 10, "bold"))

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

      
    #  GUARDAR / CARGAR / DATOS DE EJEMPLO
      

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
        except (CalidadError, OSError) as e:
            messagebox.showerror(type(e).__name__, str(e))
            return
        self.refrescar()
        self.estado.set(f"✔ Empresa cargada desde {ruta}")

    def cargar_datos_ejemplo(self):
        """Carga datos para probar: un lote pendiente (para inspeccionar en vivo) y dos
        lotes ya inspeccionados con el Simulador, para que el panel tenga datos."""
        hoy = date.today()
        e = self.empresa
        ana = e.crear_registrar_profesional("Ana")
        ana.agregar_certificacion(Certificacion("ISO", hoy - timedelta(days=30), hoy + timedelta(days=335)))
        bruno = e.crear_registrar_profesional("Bruno")
        bruno.agregar_certificacion(Certificacion("ISO", hoy - timedelta(days=90), hoy + timedelta(days=270)))
        e.crear_registrar_profesional("Carlos")  # sin certificaciones
        eq_visual = e.crear_registrar_equipo("Visual", hoy - timedelta(days=30))
        eq_dim = e.crear_registrar_equipo("Dimensional", hoy - timedelta(days=60))
        e.crear_registrar_equipo("Visual", hoy - timedelta(days=165))   # por vencer
        e.crear_registrar_equipo("Visual", hoy - timedelta(days=200))   # vencido
        proc_visual = e.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5,
                                                      certificacion_requerida="ISO")
        proc_dim = e.crear_registrar_procedimiento(ProcedimientoDimensional, limite_gravedad_acumulada=10)

        # Lote 1: queda pendiente para inspeccionar en vivo
        tornillos = e.crear_registrar_lote("Tornillos M8", 200)
        for _ in range(20):
            e.crear_registrar_muestra(10, tornillos)

        # Lotes 2 a 4: inspeccionados al azar con semilla fija (siempre dan lo mismo)
        def lote_simulado(nombre, semilla, profesional, equipo, procedimiento, dias, **opciones):
            lote = e.crear_registrar_lote(nombre, 200)
            for _ in range(20):
                e.crear_registrar_muestra(10, lote)
            Simulador(semilla).simular_lote(e, lote, profesional, equipo, procedimiento,
                                            hoy - timedelta(days=dias), **opciones)
            lote.decidir()

        lote_simulado("Arandelas", 5, ana, eq_visual, proc_visual, 3, prob_defecto=0.3)    # 10 %: rechazado
        lote_simulado("Tuercas M6", 2, bruno, eq_visual, proc_visual, 2, prob_defecto=0.3)  # 5 %: aprobado
        lote_simulado("Pernos M10", 11, bruno, eq_dim, proc_dim, 1, dispersion=0.6)         # 0 %: aprobado

        self.refrescar()
        messagebox.showinfo("Datos de ejemplo",
                            "Se cargaron:\n\n"
                            "• Tornillos M8: 20 muestras PENDIENTES para inspeccionar en vivo\n"
                            "• Arandelas (10 % → RECHAZADO), Tuercas M6 (5 % justo → APROBADO) y\n"
                            "   Pernos M10 (dimensional → APROBADO): inspeccionados al azar con semilla fija\n"
                            "• Ana y Bruno (ISO vigente) y Carlos (sin certificaciones)\n"
                            "• 4 equipos: uno de cada tipo al día, uno por vencer y uno VENCIDO\n"
                            "• Procedimiento visual (límite 5, pide ISO) y dimensional (límite 10)")

      
    #  REFRESCAR TODA LA INTERFAZ
      

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

        # Tabla de reportes (en rojo los que tienen un defecto crítico)
        self.tabla_reportes.delete(*self.tabla_reportes.get_children())
        self._reportes_por_fila = {}
        for r in e.reportes():
            maxima = max(map(lambda d: d.gravedad, r.defectos)) if r.defectos else 0
            fila = self.tabla_reportes.insert("", "end", tags=("critico",) if maxima == 5 else (),
                                              values=(id_corto(r.id), id_corto(r.muestra_id), r.fecha,
                                                      len(r.defectos), maxima))
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


if __name__ == "__main__":
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()