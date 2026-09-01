import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.reporte import Reporte


def test_creacion_reporte_guarda_datos():
    defectos = ["rayadura"]
    reporte = Reporte("M1", "L1", "P1", "2024-01-01", defectos)
    assert reporte.get_muestra_id() == "M1"
    assert reporte.get_lote_id() == "L1"
    assert reporte.get_profesional_id() == "P1"
    assert reporte.get_fecha() == "2024-01-01"
    assert reporte.get_defectos() == defectos
