"""Guardar y cargar la empresa (pickle) y cargar los datos de ejemplo."""

from tkinter import filedialog, messagebox
from datetime import date, timedelta

from classes.certificacion import Certificacion
from classes.empresa import Empresa
from classes.excepciones import CalidadError
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.simulador import Simulador


class Archivos:
    """Métodos de la ventana principal (App) para esta página.
    App hereda de esta clase, así que `self` es la App: desde acá se usan
    self.empresa, self._ejecutar(), self.refrescar(), etc."""

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