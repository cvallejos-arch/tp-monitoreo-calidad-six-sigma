import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.estado_muestra import EstadoMuestra


def test_valores_estado_muestra():
    assert EstadoMuestra.PENDIENTE.value == "PENDIENTE"
    assert EstadoMuestra.EN_INSPECCION.value == "EN_INSPECCION"
    assert EstadoMuestra.CONFORME.value == "CONFORME"
    assert EstadoMuestra.NO_CONFORME.value == "NO_CONFORME"
