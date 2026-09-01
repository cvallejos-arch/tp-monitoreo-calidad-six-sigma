import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.equipo import Equipo


def test_creacion_equipo_guarda_datos():
    equipo = Equipo(1, "Dimensional", "2024-01-01")
    assert equipo.get_id() == 1
    assert equipo.get_categoria() == "Dimensional"
    assert equipo.get_fecha_calibracion() == "2024-01-01"
