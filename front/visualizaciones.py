"""Cada función recibe los datos y devuelve grafico: una función
dibujar(canvas, ancho, alto) que se le pasa a Grafico.mostrar()."""

from front.estilos import (
    FUENTE, BLANCO, BORDE, TEXTO, SUAVE, ROJO,
    FONDO_ESTADO,
)
from front.herramientas import rectangulo_redondeado


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