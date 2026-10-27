"""Página Registro: lotes, muestras, profesionales, certificaciones, equipos y procedimientos."""

import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta

from classes.certificacion import Certificacion
from classes.excepciones import DatosInvalidosError
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual

from front.estilos import BLANCO, BORDE, FUENTE, SUAVE
from front.herramientas import Grafico, Selector, boton, leer_entero, leer_fecha, tarjeta


class PaginaRegistro:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

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
            # Empresa valida todo ANTES de crear: si no entran todas, no se crea ninguna.
            # *[unidades] * cantidad desempaqueta la lista como argumentos (*cantidades)
            creadas = self.empresa.crear_registrar_muestras(lote, *[unidades] * cantidad)
            return len(creadas)
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