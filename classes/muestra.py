class Muestra:
    def __init__(self, id, cantidad, lote_id):
        self._id = id
        self._cantidad = cantidad
        self._estado = EstadoMuestra.PENDIENTE
        self._defectos = []
        self._lote_id = lote_id
        self._inspeccion = None
        self._reporte = None

    def get_id(self):
        return self._id

    def get_cantidad(self):
        return self._cantidad

    def get_estado(self):
        return self._estado

    def get_defectos(self):
        return self._defectos

    def get_lote_id(self):
        return self._lote_id

    def get_reporte(self):
        return self._reporte

    def asignar_lote(self, lote_id):
        pass

    def iniciar_inspeccion(self):
        pass

    def agregar_defecto(self, defecto):
        pass

    def cerrar(self, limite_gravedad):
        pass

    def suma_gravedades(self):
        pass

    def tiene_critico(self):
        pass