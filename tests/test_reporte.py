"""Tests de Reporte: contenu, copie immutable des défauts, unicité."""
import pytest
from datetime import date

from classes.reporte import Reporte
from classes.defecto import Defecto


class TestCreacionReporte:
    def test_creacion_valida(self):
        defectos = [
            Defecto("VISUAL", "Rayadura", 3),
            Defecto("DIMENSIONAL", "Desviación", 4),
        ]
        reporte = Reporte("M1", "L1", "P1", date(2025, 6, 15), defectos)
        assert reporte.muestra_id == "M1"
        assert reporte.lote_id == "L1"
        assert reporte.profesional_id == "P1"
        assert reporte.fecha == date(2025, 6, 15)
        assert len(reporte.defectos) == 2


class TestCopiaInmutable:
    def test_defectos_son_copias(self):
        """Los defectos del reporte son copias, no las mismas instancias."""
        defecto_original = Defecto("VISUAL", "Rayadura", 3)
        reporte = Reporte("M1", "L1", "P1", date(2025, 6, 15), [defecto_original])
        assert reporte.defectos[0] is not defecto_original

    def test_defectos_conservan_datos(self):
        defecto_original = Defecto("VISUAL", "Rayadura", 3)
        reporte = Reporte("M1", "L1", "P1", date(2025, 6, 15), [defecto_original])
        copia = reporte.defectos[0]
        assert copia.tipo == defecto_original.tipo
        assert copia.descripcion == defecto_original.descripcion
        assert copia.gravedad == defecto_original.gravedad

    def test_defectos_es_tupla(self):
        """Los defectos del reporte están en una tupla inmutable."""
        reporte = Reporte("M1", "L1", "P1", date(2025, 6, 15),
                          [Defecto("VISUAL", "Test", 1)])
        assert isinstance(reporte.defectos, tuple)

    def test_modificar_lista_original_no_afecta_reporte(self):
        """Modificar la lista original de defectos no afecta al reporte."""
        defectos = [Defecto("VISUAL", "Rayadura", 3)]
        reporte = Reporte("M1", "L1", "P1", date(2025, 6, 15), defectos)
        defectos.append(Defecto("VISUAL", "Otro", 2))
        assert len(reporte.defectos) == 1


class TestUnicidadReporte:
    def test_cada_reporte_tiene_id_unico(self):
        defectos = [Defecto("VISUAL", "Test", 1)]
        r1 = Reporte("M1", "L1", "P1", date(2025, 6, 15), defectos)
        r2 = Reporte("M1", "L1", "P1", date(2025, 6, 15), defectos)
        assert r1.id != r2.id
