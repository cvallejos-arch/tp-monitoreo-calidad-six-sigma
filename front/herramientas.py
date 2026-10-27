"""Herramientas de la interfaz: funciones auxiliares (lectura de datos y textos)
y componentes visuales reutilizables (selector, botón, tarjeta, página con
desplazamiento y lienzo para gráficos)."""

import tkinter as tk
from tkinter import ttk
from datetime import date

from classes.excepciones import DatosInvalidosError
from front.estilos import (
    FUENTE, FONDO, BLANCO, BORDE, TEXTO, SUAVE,
    AZUL, NARANJA, NARANJA_ACTIVO, LATERAL_ACTIVO, MESES,
)


# Funciones auxiliares (lectura de datos y textos)

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


# Componentes visuales

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


class PaginaDesplazable(tk.Frame):
    """Página con barra de desplazamiento vertical. El contenido va en self.interior.
    Si entra en la ventana, ocupa todo el alto disponible y la barra no aparece;
    si no entra, aparece la barra y se puede bajar (también con la rueda del mouse)."""

    def __init__(self, padre):
        super().__init__(padre, bg=FONDO)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._lienzo = tk.Canvas(self, bg=FONDO, highlightthickness=0)
        self._lienzo.grid(row=0, column=0, sticky="nsew")
        self._barra = ttk.Scrollbar(self, orient="vertical", command=self._lienzo.yview)
        self._lienzo.configure(yscrollcommand=self._barra.set)
        self.interior = tk.Frame(self._lienzo, bg=FONDO)
        self._ventana = self._lienzo.create_window(0, 0, window=self.interior, anchor="nw")
        self._lienzo.bind("<Configure>", lambda e: self._ajustar())
        self.interior.bind("<Configure>", lambda e: self._ajustar())
        self._hace_falta = False

    def _ajustar(self):
        ancho, visible = self._lienzo.winfo_width(), self._lienzo.winfo_height()
        alto = max(visible, self.interior.winfo_reqheight())
        self._lienzo.itemconfigure(self._ventana, width=ancho, height=alto)
        self._lienzo.configure(scrollregion=(0, 0, ancho, alto))
        self._hace_falta = alto > visible + 1
        if self._hace_falta:
            self._barra.grid(row=0, column=1, sticky="ns")
        else:
            self._barra.grid_remove()
            self._lienzo.yview_moveto(0)

    def desplazar(self, unidades):
        if self._hace_falta:
            self._lienzo.yview_scroll(unidades, "units")


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