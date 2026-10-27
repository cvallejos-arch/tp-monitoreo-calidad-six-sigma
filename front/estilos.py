"""Paleta de colores, tipografía y estilos ttk."""

from tkinter import ttk


FUENTE = "Segoe UI"
LATERAL = "#1f4e8c"          
LATERAL_ACTIVO = "#2f66b0"   
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


def aplicar_estilos():
    """Configura el aspecto de los widgets ttk (entradas, listas, tablas, barras)."""
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