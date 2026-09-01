import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.inspeccion import Inspeccion
from classes.muestra import Muestra
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.procedimiento import Procedimiento


def test_creacion_inspeccion_guarda_datos():
    muestra = Muestra(1, 50, "L1")
    profesional = Profesional(2, "Ana")
    equipo = Equipo(3, "Dimensional", "2024-01-01")
    procedimiento = Procedimiento(4, 10, "Dimensional")

    inspeccion = Inspeccion(10, muestra, profesional, equipo, procedimiento, "2024-02-01")

    assert inspeccion.get_id() == 10
    assert inspeccion.get_muestra_id() == 1
    assert inspeccion.get_profesional_id() == 2
    assert inspeccion.get_equipo_id() == 3
    assert inspeccion.get_procedimiento_id() == 4
    assert inspeccion.get_fecha() == "2024-02-01"
    assert inspeccion.get_defectos() == []
