from lote import Lote

class Empresa:
    def __init__(self):
        self._lotes = []
        self._muestras = []
        self._profesionales = []
        self._equipos = []
        self._procedimientos = []
        self._inspecciones = []

    def crear_registrar_lote(self):
        lote = Lote()
        self._lotes.append(lote)

    def crear_registrar_muestra(self):
        muestra = Muestra()
        self._muestras.append(muestra)

    def crear_registrar_profesional(self):
        profesional = Profesional()
        self._profesionales.append(profesional)

    def crear_registrar_equipo(self):
        equipo = Equipo()
        self._equipos.append(equipo)

    def crear_registrar_procedimiento(self):
        procedimiento = Procedimiento()
        self._procedimientos.append(procedimiento)

    def crear_registrar_inspeccion(self):
        inspeccion = Inspeccion()
        self._inspecciones.append(inspeccion)




    def lanzar_inspeccion(self, muestra, profesional, equipo, procedimiento, fecha):
        pass


if __name__ == "__main__":
    main()

# dentro del main()
Tech_2 = Empresa()
Tech_2.registrar_lote
