from classes.procedimiento import Procedimiento
from classes.defecto import DefectoVisual


class ProcedimientoVisual(Procedimiento):
    """Evalúa observaciones cualitativas del operario y genera defectos VISUAL."""

    CLASE_DEFECTO = DefectoVisual

    def __init__(self, **kwargs):
        # Si no se indica la categoría de equipo, por defecto es "Visual"
        kwargs.setdefault("categoria_equipo_requerida", "Visual")
        super().__init__(**kwargs)

    def evaluar(self, observaciones):
        """Evalúa cada observación visual. Si defecto_detectado es True,
        genera un defecto con la gravedad indicada."""
        # Primero se filtran las observaciones con defecto detectado.
        # Luego cada observación filtrada se transforma en un DefectoVisual.
        return list(
            map(
                lambda obs: DefectoVisual(
                    descripcion=obs.descripcion,
                    gravedad=obs.gravedad
                ),
                filter(lambda obs: obs.defecto_detectado, observaciones)
            )
        )
