import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.muestra import Muestra
from classes.estado_muestra import EstadoMuestra


def test_creacion_muestra_guarda_datos():
    muestra = Muestra(1, 50, "L1")
    assert muestra.get_id() == 1
    assert muestra.get_cantidad() == 50
    assert muestra.get_lote_id() == "L1"


def test_creacion_muestra_estado_inicial():
    muestra = Muestra(1, 50, "L1")
    assert muestra.get_estado() == EstadoMuestra.PENDIENTE
    assert muestra.get_defectos() == []
    assert muestra.get_reporte() is None
