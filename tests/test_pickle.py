"""Tests de serialización con pickle: guardar y cargar la Empresa completa, y retomar
el trabajo donde quedó. Usa tmp_path (carpeta temporal de pytest)."""
import pickle
import pytest
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.defecto import DefectoVisual
from classes.estado_muestra import EstadoMuestra
from classes.estado_lote import EstadoLote
from classes.excepciones import DatosInvalidosError, CertificacionNoVigenteError

FECHA = date(2025, 6, 15)


@pytest.fixture
def contexto():
    """Empresa con un lote de 3 muestras: la primera ya inspeccionada (no conforme)
    y las otras dos pendientes en la cola."""
    empresa = Empresa()
    lote = empresa.crear_registrar_lote("Tornillos", 100)
    for _ in range(3):
        empresa.crear_registrar_muestra(10, lote)
    ana = empresa.crear_registrar_profesional("Ana")
    ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
    equipo = empresa.crear_registrar_equipo("Visual", FECHA - timedelta(days=10))
    proc = empresa.crear_registrar_procedimiento(
        ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO"
    )

    insp = empresa.lanzar_siguiente_inspeccion(lote, ana, equipo, proc, FECHA)
    insp.ejecutar([ObservacionVisual("Fractura", True, 5)])
    insp.cerrar()
    return empresa


def _guardar_y_cargar(empresa, tmp_path):
    ruta = tmp_path / "empresa.pkl"
    empresa.guardar(ruta)
    return Empresa.cargar(ruta)


class TestGuardarYCargar:
    def test_crea_archivo_binario(self, contexto, tmp_path):
        ruta = tmp_path / "empresa.pkl"
        contexto.guardar(ruta)
        assert ruta.exists()
        assert ruta.read_bytes()[:1] == b"\x80"   # los pickles empiezan con este byte

    def test_carga_una_empresa_nueva_igual(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        assert isinstance(cargada, Empresa)
        assert cargada is not contexto
        assert cargada.resumen() == contexto.resumen()

    def test_conserva_ids_y_estados(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        lote_original = contexto.listar_lotes()[0]
        lote_cargado = cargada.obtener_lote(lote_original.id)

        assert lote_cargado is not None
        estados = list(map(lambda m: m.estado, lote_cargado.muestras))
        assert estados == [EstadoMuestra.NO_CONFORME, EstadoMuestra.PENDIENTE,
                           EstadoMuestra.PENDIENTE]

    def test_conserva_pila_de_estados_y_reporte(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        muestra = cargada.listar_muestras(estado=EstadoMuestra.NO_CONFORME)[0]

        assert muestra.historial_estados == (
            EstadoMuestra.PENDIENTE, EstadoMuestra.EN_INSPECCION, EstadoMuestra.NO_CONFORME
        )
        assert isinstance(muestra.reporte.defectos[0], DefectoVisual)
        assert len(cargada.reportes()) == 1

    def test_conserva_certificaciones_y_fechas(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        ana = list(cargada._registros["profesionales"].values())[0]
        assert ana.tiene_certificacion_vigente("ISO", FECHA) is True

    def test_conserva_relaciones_entre_objetos(self, contexto, tmp_path):
        """La muestra del registro y la del lote siguen siendo el MISMO objeto."""
        cargada = _guardar_y_cargar(contexto, tmp_path)
        lote = cargada.listar_lotes()[0]
        primera = lote.muestras[0]
        assert cargada.obtener_muestra(primera.id) is primera


class TestRetomarElTrabajo:
    def test_la_cola_sigue_donde_quedo(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        lote = cargada.listar_lotes()[0]
        assert len(lote.pendientes_en_orden()) == 2
        assert lote.siguiente_muestra_pendiente() is lote.muestras[1]

    def test_terminar_las_inspecciones_y_decidir(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        lote = cargada.listar_lotes()[0]
        ana = list(cargada._registros["profesionales"].values())[0]
        equipo = list(cargada._registros["equipos"].values())[0]
        proc = list(cargada._registros["procedimientos"].values())[0]

        for _ in range(2):
            insp = cargada.lanzar_siguiente_inspeccion(lote, ana, equipo, proc, FECHA)
            insp.ejecutar([ObservacionVisual("Sin defectos", False)])
            insp.cerrar()

        # 1 de 3 no conforme = 33 % > 5 %
        assert lote.decidir() == EstadoLote.RECHAZADO

    def test_las_validaciones_siguen_funcionando(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        lote = cargada.listar_lotes()[0]
        sin_cert = cargada.crear_registrar_profesional("Carlos")
        equipo = list(cargada._registros["equipos"].values())[0]
        proc = list(cargada._registros["procedimientos"].values())[0]
        with pytest.raises(CertificacionNoVigenteError):
            cargada.lanzar_siguiente_inspeccion(lote, sin_cert, equipo, proc, FECHA)

    def test_el_original_no_cambia(self, contexto, tmp_path):
        cargada = _guardar_y_cargar(contexto, tmp_path)
        cargada.crear_registrar_lote("Tuercas", 50)
        assert len(contexto.listar_lotes()) == 1
        assert len(cargada.listar_lotes()) == 2


class TestArchivosInvalidos:
    def test_archivo_inexistente(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            Empresa.cargar(tmp_path / "no_existe.pkl")

    def test_archivo_que_no_es_pickle(self, tmp_path):
        ruta = tmp_path / "texto.pkl"
        ruta.write_text("esto no es un pickle", encoding="utf-8")
        with pytest.raises(DatosInvalidosError):
            Empresa.cargar(ruta)

    def test_archivo_vacio(self, tmp_path):
        ruta = tmp_path / "vacio.pkl"
        ruta.write_bytes(b"")
        with pytest.raises(DatosInvalidosError):
            Empresa.cargar(ruta)

    def test_pickle_de_otro_objeto(self, tmp_path):
        ruta = tmp_path / "lista.pkl"
        with open(ruta, "wb") as f:
            pickle.dump([1, 2, 3], f)
        with pytest.raises(DatosInvalidosError) as exc:
            Empresa.cargar(ruta)
        assert "list" in str(exc.value)
