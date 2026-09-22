"""Tests de Procedimiento: évaluation polymorphe dimensional/visual."""
import pytest

from classes.procedimiento import Procedimiento
from classes.proc_dimensional import ProcedimientoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.observacion_visual import ObservacionVisual
from classes.excepciones import DatosInvalidosError


class TestCreacionProcedimiento:
    def test_creacion_sin_certificacion(self):
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        assert proc.limite_gravedad_acumulada == 5
        assert proc.categoria_equipo_requerida == "Visual"
        assert proc.certificacion_requerida is None

    def test_creacion_con_certificacion(self):
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual",
            certificacion_requerida="ISO"
        )
        assert proc.certificacion_requerida == "ISO"

    def test_limite_negativo_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            ProcedimientoVisual(
                limite_gravedad_acumulada=-1,
                categoria_equipo_requerida="Visual"
            )

    def test_limite_cero_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            ProcedimientoVisual(
                limite_gravedad_acumulada=0,
                categoria_equipo_requerida="Visual"
            )

    def test_base_no_implementa_evaluar(self):
        proc = Procedimiento(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        with pytest.raises(NotImplementedError):
            proc.evaluar([])


class TestProcedimientoVisual:
    def test_sin_defectos(self):
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        obs = [ObservacionVisual("OK", False)]
        defectos = proc.evaluar(obs)
        assert len(defectos) == 0

    def test_con_defecto(self):
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        obs = [ObservacionVisual("Rayadura visible", True, 3)]
        defectos = proc.evaluar(obs)
        assert len(defectos) == 1
        assert defectos[0].tipo == "VISUAL"
        assert defectos[0].gravedad == 3

    def test_multiples_observaciones(self):
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        obs = [
            ObservacionVisual("OK", False),
            ObservacionVisual("Rayadura", True, 2),
            ObservacionVisual("Grieta", True, 4),
        ]
        defectos = proc.evaluar(obs)
        assert len(defectos) == 2


class TestProcedimientoDimensional:
    def test_sin_desviacion(self):
        proc = ProcedimientoDimensional(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Dimensional"
        )
        obs = [ObservacionDimensional(9.5, 9.0, 10.0, "Pieza dentro de rango")]
        defectos = proc.evaluar(obs)
        assert len(defectos) == 0

    def test_con_desviacion(self):
        proc = ProcedimientoDimensional(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Dimensional"
        )
        obs = [ObservacionDimensional(10.5, 9.0, 10.0, "Pieza fuera de rango")]
        defectos = proc.evaluar(obs)
        assert len(defectos) == 1
        assert defectos[0].tipo == "DIMENSIONAL"

    def test_polimorfismo_misma_interfaz(self):
        """Les deux types de procédure répondent à la même opération evaluar()."""
        proc_v = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Visual"
        )
        proc_d = ProcedimientoDimensional(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Dimensional"
        )

        obs_v = [ObservacionVisual("Test", True, 3)]
        obs_d = [ObservacionDimensional(11.0, 9.0, 10.0, "Test")]

        # Ambos responden a evaluar() de forma polimórfica
        assert len(proc_v.evaluar(obs_v)) == 1
        assert len(proc_d.evaluar(obs_d)) == 1
