import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.procedimiento import Procedimiento, ProcedimientoDimensional, ProcedimientoVisual


def test_creacion_procedimiento_guarda_datos():
    proc = Procedimiento(1, 10, "Dimensional", "ISO9001")
    assert proc.get_id() == 1
    assert proc.get_limite_gravedad_acumulada() == 10
    assert proc.get_categoria_equipo_requerida() == "Dimensional"
    assert proc.get_certificacion_requerida() == "ISO9001"


def test_creacion_procedimiento_certificacion_por_defecto():
    proc = Procedimiento(1, 10, "Dimensional")
    assert proc.get_certificacion_requerida() is None


def test_subclases_heredan_getters():
    dimensional = ProcedimientoDimensional(1, 10, "Dimensional")
    visual = ProcedimientoVisual(2, 5, "Visual")
    assert dimensional.get_id() == 1
    assert visual.get_id() == 2
