import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.profesional import Profesional


def test_creacion_profesional_guarda_datos():
    profesional = Profesional(1, "Ana")
    assert profesional.get_id() == 1
    assert profesional.get_nombre() == "Ana"
