"""Tests de conjuntos (clase 9): __eq__ y __hash__ por id en las entidades (Entidad)
y las operaciones con set del dominio (&, ^, -, update)."""
import pickle
import pytest
from datetime import date, timedelta

from classes.entidad import Entidad
from classes.empresa import Empresa
from classes.lote import Lote
from classes.muestra import Muestra
from classes.profesional import Profesional
from classes.equipo import Equipo
from classes.reporte import Reporte
from classes.defecto import Defecto, DefectoVisual
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.excepciones import DatosInvalidosError

FECHA = date(2025, 6, 15)


class TestIgualdadPorId:
    def test_todas_las_entidades_heredan_de_entidad(self):
        for clase in (Lote, Muestra, Profesional, Equipo, Reporte, ProcedimientoVisual):
            assert issubclass(clase, Entidad)

    def test_objetos_distintos_no_son_iguales(self):
        assert Profesional("Ana") != Profesional("Ana")    # mismo nombre, distinto id

    def test_misma_entidad_cargada_con_pickle_es_igual(self):
        """Después de pickle es OTRO objeto (is da False), pero la misma entidad (== da True)."""
        lote = Lote("Tornillos", 100)
        copia = pickle.loads(pickle.dumps(lote))
        assert copia is not lote
        assert copia == lote
        assert hash(copia) == hash(lote)                   # a == b implica hash(a) == hash(b)

    def test_reporte_cargado_desde_json_es_igual_al_original(self):
        original = Reporte("M1", "L1", "P1", FECHA, [DefectoVisual("Fisura", 5)])
        cargado = Reporte.from_dict(original.to_dict())    # el id viaja como texto
        assert cargado is not original
        assert cargado == original
        assert hash(cargado) == hash(original)

    def test_tipos_distintos_no_son_iguales(self):
        """Aunque coincidiera el id, un Lote nunca es igual a una Muestra."""
        lote = Lote("Tornillos", 100)
        muestra = Muestra(10, lote.id)
        muestra._id = lote.id                              # forzado solo para el test
        assert lote != muestra

    def test_comparar_con_algo_que_no_es_entidad(self):
        assert Lote("Tornillos", 100) != "Tornillos"

    def test_hash_estable(self):
        """El hash no cambia aunque cambie el estado: depende solo del id."""
        lote = Lote("Tornillos", 100)
        antes = hash(lote)
        lote.crear_muestra(10)
        assert hash(lote) == antes


class TestEntidadesEnSets:
    def test_set_sin_duplicados(self):
        ana = Profesional("Ana")
        copia = pickle.loads(pickle.dumps(ana))
        assert len({ana, copia, ana}) == 1

    def test_pertenencia_con_in(self):
        equipo = Equipo("Visual", FECHA)
        equipos = {equipo, Equipo("Dimensional", FECHA)}
        assert pickle.loads(pickle.dumps(equipo)) in equipos

    def test_como_clave_de_diccionario(self):
        lote = Lote("Tornillos", 100)
        estados = {lote: "en producción"}
        assert estados[pickle.loads(pickle.dumps(lote))] == "en producción"

    def test_reportes_originales_y_cargados_son_el_mismo_conjunto(self, tmp_path):
        empresa = _empresa_con_dos_lotes()[0]
        ruta = tmp_path / "reportes.json"
        empresa.exportar_reportes_json(ruta)
        assert set(empresa.reportes()) == set(Empresa.cargar_reportes_json(ruta))


class TestDefectoNoSeComparaPorValor:
    def test_dos_defectos_iguales_son_dos_defectos(self):
        """Dos rayaduras de gravedad 2 son dos defectos distintos: un set no las fusiona."""
        a = Defecto("VISUAL", "Rayadura", 2)
        b = Defecto("VISUAL", "Rayadura", 2)
        assert a != b
        assert len({a, b}) == 2


def _empresa_con_dos_lotes():
    """Lote A (visual): Ana y Beto, con defectos VISUAL. Lote B: Ana con defectos
    VISUAL y Carla con defectos DIMENSIONAL."""
    empresa = Empresa()
    lote_a = empresa.crear_registrar_lote("Tornillos", 100)
    lote_b = empresa.crear_registrar_lote("Tuercas", 100)
    a1, a2 = empresa.crear_registrar_muestras(lote_a, 10, 10)
    b1, b2 = empresa.crear_registrar_muestras(lote_b, 10, 10)

    def certificado(nombre):
        p = empresa.crear_registrar_profesional(nombre)
        p.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
        return p

    ana, beto, carla = certificado("Ana"), certificado("Beto"), certificado("Carla")
    visual = empresa.crear_registrar_equipo("Visual", FECHA - timedelta(days=10))
    dimensional = empresa.crear_registrar_equipo("Dimensional", FECHA - timedelta(days=10))
    proc_v = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)
    proc_d = empresa.crear_registrar_procedimiento(ProcedimientoDimensional, limite_gravedad_acumulada=5)

    casos = [
        (a1, ana, visual, proc_v, [ObservacionVisual("Fisura", True, 5)]),
        (a2, beto, visual, proc_v, [ObservacionVisual("Mancha", True, 1)]),
        (b1, ana, visual, proc_v, [ObservacionVisual("Raya", True, 2)]),
        (b2, carla, dimensional, proc_d, [ObservacionDimensional(10.5, 9.0, 10.0, "Larga")]),
    ]
    for muestra, prof, equipo, proc, observaciones in casos:
        insp = empresa.lanzar_inspeccion(muestra, prof, equipo, proc, FECHA)
        insp.ejecutar(observaciones)
        insp.cerrar()
    return empresa, lote_a, lote_b, ana, beto, carla, visual, dimensional


class TestTiposDeDefecto:
    def test_tipos_sin_repetir(self):
        _, lote_a, lote_b, *_ = _empresa_con_dos_lotes()
        assert lote_a.tipos_de_defecto() == {"VISUAL"}
        assert lote_b.tipos_de_defecto() == {"VISUAL", "DIMENSIONAL"}

    def test_interseccion_y_diferencia_simetrica(self):
        _, lote_a, lote_b, *_ = _empresa_con_dos_lotes()
        assert lote_a.tipos_en_comun(lote_b) == {"VISUAL"}
        assert lote_a.tipos_exclusivos(lote_b) == {"DIMENSIONAL"}

    def test_lote_sin_muestras_cerradas(self):
        lote = Lote("Vacío", 100)
        lote.crear_muestra(10)
        assert lote.tipos_de_defecto() == set()

    def test_comparar_con_algo_que_no_es_lote(self):
        with pytest.raises(DatosInvalidosError):
            Lote("Tornillos", 100).tipos_en_comun("otro")


class TestProfesionalesYEquiposDeLote:
    def test_profesionales_de_cada_lote(self):
        empresa, lote_a, lote_b, ana, beto, carla, *_ = _empresa_con_dos_lotes()
        assert empresa.profesionales_de_lote(lote_a) == {ana, beto}
        assert empresa.profesionales_de_lote(lote_b) == {ana, carla}

    def test_en_comun_y_solo_en_uno(self):
        empresa, lote_a, lote_b, ana, beto, carla, *_ = _empresa_con_dos_lotes()
        assert empresa.profesionales_en_comun(lote_a, lote_b) == {ana}
        assert empresa.profesionales_solo_en(lote_a, lote_b) == {beto}
        assert empresa.profesionales_solo_en(lote_b, lote_a) == {carla}

    def test_equipos_de_lote(self):
        empresa, lote_a, lote_b, *_, visual, dimensional = _empresa_con_dos_lotes()
        assert empresa.equipos_de_lote(lote_a) == {visual}
        assert empresa.equipos_de_lote(lote_b) == {visual, dimensional}

    def test_lote_sin_inspecciones(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Nuevo", 10)
        assert empresa.profesionales_de_lote(lote) == set()

    def test_funciona_despues_de_cargar_con_pickle(self, tmp_path):
        empresa, lote_a, lote_b, ana, *_ = _empresa_con_dos_lotes()
        ruta = tmp_path / "empresa.pkl"
        empresa.guardar(ruta)
        cargada = Empresa.cargar(ruta)
        lote_a_cargado = cargada.obtener_lote(lote_a.id)
        lote_b_cargado = cargada.obtener_lote(lote_b.id)
        # los objetos cargados son otros, pero iguales por id a los originales
        assert cargada.profesionales_en_comun(lote_a_cargado, lote_b_cargado) == {ana}
