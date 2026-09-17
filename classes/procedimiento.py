import uuid
from classes.validacion import validar_texto, validar_entero

class Procedimiento:
      def __init__(self, limite_gravedad_acumulada, categoria_equipo_requerida, certificacion_requerida=None):
            validar_texto(categoria_equipo_requerida)
            validar_entero(limite_gravedad_acumulada)
            if certificacion_requerida is not None:
                  validar_texto(certificacion_requerida)

            self._id = uuid.uuid4()
            self._limite_gravedad_acumulada = limite_gravedad_acumulada
            self._categoria_equipo_requerida = categoria_equipo_requerida
            self._certificacion_requerida = certificacion_requerida

      @property
      def id(self):
            return self._id

      @property
      def limite_gravedad_acumulada(self):
            return self._limite_gravedad_acumulada

      @property
      def categoria_equipo_requerida(self):
            return self._categoria_equipo_requerida

      @property
      def certificacion_requerida(self):
            return self._certificacion_requerida

      def evaluar(self, observaciones):
            raise NotImplementedError("Se implementa en las subclases")

      def __repr__(self):
            return (
                  "Procedimiento(id=" + str(self._id) +
                  ", limite_gravedad_acumulada=" + str(self._limite_gravedad_acumulada) +
                  ", categoria_equipo_requerida=" + self._categoria_equipo_requerida +
                  ", certificacion_requerida=" + str(self._certificacion_requerida) +
                  ")"
            )