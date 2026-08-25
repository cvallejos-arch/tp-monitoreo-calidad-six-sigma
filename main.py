class Administrador:
    def __init__(self):
        self._lotes = []
        self._muestras = []
        self._profesionales = []
        self._equipos = []
        self._procedimientos = []
        self._inspecciones = []

    def registrar_lote(self, id, cantidad):
        pass

    def registrar_muestra(self, id, cantidad):
        pass

    def registrar_profesional(self, id, nombre):
        pass

    def registrar_equipo(self, id, categoria, fecha_calibracion):
        pass

    def registrar_procedimiento(self, proc):
        pass

    def lanzar_inspeccion(self, muestra, profesional, equipo, procedimiento, fecha):
        pass


if __name__ == "__main__":
    main()

