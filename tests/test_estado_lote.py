import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classes.lote import Lote
from classes.estado_lote import EstadoLote


def test_creacion_lote_guarda_datos():
    lote = Lote(1, 100)
    assert lote.get_id() == 1
    assert lote.get_cantidad_fabricada() == 100


def test_creacion_lote_estado_inicial():
    lote = Lote(1, 100)
    assert lote.get_estado() == EstadoLote.EN_PRODUCCION
    assert lote.get_muestras() == []
