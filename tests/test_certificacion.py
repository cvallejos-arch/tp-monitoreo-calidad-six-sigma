import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.validacion import validar_entero


def test_validar_entero_con_entero():
    assert validar_entero(5) is True


def test_validar_entero_con_no_entero():
    assert validar_entero("5") is False
