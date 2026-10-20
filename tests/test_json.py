"""Tests de serialización JSON: to_dict() / Clase(**data) en Defecto y Reporte,
y exportación / carga de reportes desde Empresa. Usa tmp_path (carpeta temporal
de pytest) para no dejar archivos en el repo."""
import json
import pytest
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.defecto import Defecto, DefectoVisual, DefectoDimensional
from classes.reporte import Reporte
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError

FECHA = date(2025, 6, 15)


@pytest.fixture
def reporte():
    return Reporte(
        "M1", "L1", "P1", FECHA,
        [DefectoVisual("Fractura", 5), DefectoDimensional("Fuera", 2, 10.5, 9.0, 10.0)],
        historial_estados=(EstadoMuestra.PENDIENTE, EstadoMuestra.EN_INSPECCION,
                           EstadoMuestra.NO_CONFORME),
    )


@pytest.fixture
def empresa_con_un_reporte():
    """Empresa con 2 muestras inspeccionadas: una no conforme (con reporte) y una conforme."""
    empresa = Empresa()
    lote = empresa.crear_registrar_lote("Tornillos", 100)
    empresa.crear_registrar_muestra(10, lote)
    empresa.crear_registrar_muestra(10, lote)
    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    equipo = empresa.crear_registrar_equipo("Visual", FECHA - timedelta(days=10))
    proc = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)

    for observacion in (ObservacionVisual("Fractura", True, 5),
                        ObservacionVisual("Sin defectos", False)):
        insp = empresa.lanzar_siguiente_inspeccion(lote, ana, equipo, proc, FECHA)
        insp.ejecutar([observacion])
        insp.cerrar()
    return empresa


class TestDefectoToDict:
    def test_defecto_visual(self):
        assert DefectoVisual("Mancha", 3).to_dict() == {
            "tipo": "VISUAL", "descripcion": "Mancha", "gravedad": 3
        }

    def test_defecto_dimensional_incluye_medicion(self):
        datos = DefectoDimensional("Fuera", 2, 10.5, 9.0, 10.0, "mm").to_dict()
        assert datos["tipo"] == "DIMENSIONAL"
        assert datos["valor_medido"] == 10.5
        assert datos["unidad"] == "mm"

    @pytest.mark.parametrize("defecto", [
        Defecto("OTRO", "Genérico", 1),
        DefectoVisual("Mancha", 3),
        DefectoDimensional("Fuera", 2, 10.5, 9.0, 10.0),
    ])
    def test_ida_y_vuelta_conserva_clase_y_datos(self, defecto):
        reconstruido = Defecto.from_dict(defecto.to_dict())
        assert type(reconstruido) is type(defecto)
        assert reconstruido.to_dict() == defecto.to_dict()

    def test_from_dict_no_modifica_el_dict(self):
        datos = DefectoVisual("Mancha", 3).to_dict()
        Defecto.from_dict(datos)
        assert "tipo" in datos

    def test_dict_es_serializable_a_json(self):
        texto = json.dumps(DefectoDimensional("Fuera", 2, 10.5, 9.0, 10.0).to_dict())
        assert json.loads(texto)["valor_medido"] == 10.5


class TestReporteToDict:
    def test_tipos_compatibles_con_json(self, reporte):
        datos = reporte.to_dict()
        assert datos["fecha"] == "2025-06-15"
        assert datos["historial_estados"] == ["PENDIENTE", "EN_INSPECCION", "NO_CONFORME"]
        assert isinstance(datos["reporte_id"], str)
        assert len(datos["defectos"]) == 2
        json.dumps(datos)   # no lanza TypeError

    def test_ida_y_vuelta(self, reporte):
        reconstruido = Reporte.from_dict(reporte.to_dict())
        assert reconstruido.to_dict() == reporte.to_dict()
        assert reconstruido.fecha == FECHA
        assert reconstruido.historial_estados[-1] == EstadoMuestra.NO_CONFORME
        assert isinstance(reconstruido.defectos[1], DefectoDimensional)

    def test_conserva_el_id_original(self, reporte):
        assert str(Reporte.from_dict(reporte.to_dict()).id) == str(reporte.id)


class TestEmpresaJson:
    def test_reportes_solo_de_no_conformes(self, empresa_con_un_reporte):
        assert len(empresa_con_un_reporte.reportes()) == 1

    def test_exportar_crea_json_legible(self, empresa_con_un_reporte, tmp_path):
        ruta = tmp_path / "reportes.json"
        cantidad = empresa_con_un_reporte.exportar_reportes_json(ruta)

        assert cantidad == 1
        contenido = json.loads(ruta.read_text(encoding="utf-8"))
        assert contenido[0]["defectos"][0]["descripcion"] == "Fractura"

    def test_exportar_y_cargar(self, empresa_con_un_reporte, tmp_path):
        ruta = tmp_path / "reportes.json"
        empresa_con_un_reporte.exportar_reportes_json(ruta)

        cargados = Empresa.cargar_reportes_json(ruta)
        original = empresa_con_un_reporte.reportes()[0]

        assert len(cargados) == 1
        assert cargados[0].to_dict() == original.to_dict()

    def test_exportar_sin_reportes_genera_lista_vacia(self, tmp_path):
        ruta = tmp_path / "vacio.json"
        assert Empresa().exportar_reportes_json(ruta) == 0
        assert Empresa.cargar_reportes_json(ruta) == []

    def test_archivo_inexistente(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            Empresa.cargar_reportes_json(tmp_path / "no_existe.json")

    def test_archivo_que_no_es_json(self, tmp_path):
        ruta = tmp_path / "roto.json"
        ruta.write_text("esto no es json", encoding="utf-8")
        with pytest.raises(DatosInvalidosError):
            Empresa.cargar_reportes_json(ruta)

    def test_json_que_no_es_lista(self, tmp_path):
        ruta = tmp_path / "objeto.json"
        ruta.write_text('{"reporte": 1}', encoding="utf-8")
        with pytest.raises(DatosInvalidosError):
            Empresa.cargar_reportes_json(ruta)

    def test_reporte_incompleto(self, tmp_path):
        ruta = tmp_path / "incompleto.json"
        ruta.write_text('[{"muestra_id": "M1"}]', encoding="utf-8")
        with pytest.raises(DatosInvalidosError):
            Empresa.cargar_reportes_json(ruta)
