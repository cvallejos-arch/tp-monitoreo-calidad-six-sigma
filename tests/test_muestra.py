import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.defecto import Defecto


def test_creacion_defecto_guarda_datos():
    defecto = Defecto("Rayadura", "Rayadura superficial", 3)
    assert defecto.get_tipo() == "Rayadura"
    assert defecto.get_descripcion() == "Rayadura superficial"
    assert defecto.get_gravedad() == 3
