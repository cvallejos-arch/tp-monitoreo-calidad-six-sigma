"""Tests de reglas de la consigna que no estaban cubiertas:
- Regla 1: identificadores únicos dentro de cada categoría.
- Regla 3: datos específicos de cada tipo de defecto, coherentes con su procedimiento.
- Regla 7: un procedimiento no puede registrar defectos ajenos.
- Nombres técnicos con números y separadores (ej. 'ISO 9001').
- Cierre de inspección consistente si falla el cierre de la muestra."""
import pytest
from datetime import date, timedelta

from classes.empresa import Empresa
from classes.lote import Lote
from classes.equipo import Equipo
from classes.profesional import Profesional
from classes.certificacion import Certificacion
from classes.inspeccion import Inspeccion
from classes.defecto import Defecto, DefectoVisual, DefectoDimensional
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.observacion_visual import ObservacionVisual
from classes.observacion_dimensional import ObservacionDimensional
from classes.reporte import Reporte
from classes.validacion import validar_nombre_tecnico
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError, InspeccionInvalidaError

FECHA = date(2025, 6, 15)


# --- Regla 1: identificadores únicos ---

class TestIdentificadoresUnicos:
    def test_ids_unicos_en_cada_categoria(self):
        """Los ids son uuid4: se generan solos, nunca vacíos ni repetidos.
        Un set elimina duplicados, así que si su tamaño es igual a la cantidad
        de objetos creados, no hubo ids repetidos."""
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 10000)
        for _ in range(100):
            empresa.crear_registrar_muestra(1, lote)
            empresa.crear_registrar_profesional("Ana")
            empresa.crear_registrar_equipo("Visual", FECHA)

        for categoria in ("muestras", "profesionales", "equipos"):
            objetos = empresa._registros[categoria].values()
            ids = set(map(lambda obj: obj.id, objetos))
            assert len(ids) == 100

    def test_ids_de_muestras_unicos_dentro_del_lote(self):
        lote = Lote("Tornillos", 100)
        muestras = list(map(lambda _: lote.crear_muestra(1), range(50)))
        assert len(set(map(lambda m: m.id, muestras))) == 50

    def test_id_no_vacio(self):
        assert str(Lote("Tornillos", 10).id) != ""

    def test_registro_indexado_por_id(self):
        """El registro de Empresa es un dict {id: objeto}: no puede haber dos claves iguales."""
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 10)
        assert empresa.obtener_lote(lote.id) is lote


# --- Regla 3: defectos con datos propios de su tipo ---

class TestDefectoVisual:
    def test_tipo_fijo_visual(self):
        d = DefectoVisual("Rayadura", 2)
        assert d.tipo == "VISUAL"
        assert isinstance(d, Defecto)

    def test_copia_conserva_la_subclase(self):
        d = DefectoVisual("Rayadura", 2)
        copia = d.copia()
        assert type(copia) is DefectoVisual
        assert copia is not d
        assert (copia.descripcion, copia.gravedad) == ("Rayadura", 2)


class TestDefectoDimensional:
    def test_guarda_la_medicion(self):
        d = DefectoDimensional("Fuera de rango", 3, 10.5, 9.0, 10.0, "mm")
        assert d.tipo == "DIMENSIONAL"
        assert (d.valor_medido, d.tolerancia_min, d.tolerancia_max) == (10.5, 9.0, 10.0)
        assert d.unidad == "mm"

    def test_valor_dentro_de_tolerancia_rechazado(self):
        """Coherencia: un defecto dimensional solo existe si la medida está fuera de rango."""
        with pytest.raises(DatosInvalidosError):
            DefectoDimensional("No es defecto", 1, 9.5, 9.0, 10.0)

    @pytest.mark.parametrize("valor", [9.0, 10.0])
    def test_valor_en_el_limite_no_es_defecto(self, valor):
        with pytest.raises(DatosInvalidosError):
            DefectoDimensional("En el límite", 1, valor, 9.0, 10.0)

    def test_tolerancias_invertidas_rechazadas(self):
        with pytest.raises(DatosInvalidosError):
            DefectoDimensional("Rango invertido", 1, 11.0, 10.0, 9.0)

    def test_valor_no_numerico_rechazado(self):
        with pytest.raises(DatosInvalidosError):
            DefectoDimensional("Texto", 1, "11", 9.0, 10.0)

    def test_copia_conserva_la_medicion(self):
        d = DefectoDimensional("Fuera de rango", 3, 10.5, 9.0, 10.0, "mm")
        copia = d.copia()
        assert type(copia) is DefectoDimensional
        assert copia.valor_medido == 10.5
        assert copia is not d

    def test_reporte_conserva_los_datos_especificos(self):
        d = DefectoDimensional("Fuera de rango", 5, 12.0, 9.0, 10.0)
        reporte = Reporte("M1", "L1", "P1", FECHA, [d])
        assert isinstance(reporte.defectos[0], DefectoDimensional)
        assert reporte.defectos[0].valor_medido == 12.0


class TestProcedimientosProducenSuTipo:
    def test_visual_produce_defectos_visuales(self):
        proc = ProcedimientoVisual(limite_gravedad_acumulada=5)
        defectos = proc.evaluar([ObservacionVisual("Mancha", True, 2)])
        assert all(map(lambda d: isinstance(d, DefectoVisual), defectos))

    def test_dimensional_produce_defectos_dimensionales_con_medicion(self):
        proc = ProcedimientoDimensional(limite_gravedad_acumulada=5, unidad_medida="cm")
        defectos = proc.evaluar([ObservacionDimensional(10.5, 9.0, 10.0, "Pieza")])
        assert isinstance(defectos[0], DefectoDimensional)
        assert defectos[0].valor_medido == 10.5
        assert defectos[0].unidad == "cm"


# --- Regla 7: no registrar defectos ajenos ---

def _inspeccion_visual(procedimiento):
    """Arma una inspección válida (profesional certificado y equipo calibrado)."""
    lote = Lote("Tornillos", 100)
    muestra = lote.crear_muestra(10)
    profesional = Profesional("Ana")
    equipo = Equipo("Visual", FECHA - timedelta(days=10))
    return Inspeccion(muestra, profesional, equipo, procedimiento, FECHA), muestra


class ProcedimientoVisualDefectuoso(ProcedimientoVisual):
    """Procedimiento de prueba que, por error, devuelve un defecto dimensional."""

    def evaluar(self, observaciones):
        return [
            DefectoVisual("Mancha", 1),
            DefectoDimensional("Ajeno", 2, 11.0, 9.0, 10.0),
        ]


class TestDefectosAjenos:
    def test_defecto_ajeno_rechazado(self):
        inspeccion, _ = _inspeccion_visual(
            ProcedimientoVisualDefectuoso(limite_gravedad_acumulada=5)
        )
        with pytest.raises(InspeccionInvalidaError):
            inspeccion.ejecutar([])

    def test_rechazo_no_agrega_ningun_defecto(self):
        """Se valida todo antes de agregar: la muestra no queda a medias."""
        inspeccion, muestra = _inspeccion_visual(
            ProcedimientoVisualDefectuoso(limite_gravedad_acumulada=5)
        )
        with pytest.raises(InspeccionInvalidaError):
            inspeccion.ejecutar([])
        assert muestra.defectos == ()

    def test_defectos_del_tipo_correcto_se_agregan(self):
        inspeccion, muestra = _inspeccion_visual(
            ProcedimientoVisual(limite_gravedad_acumulada=5)
        )
        inspeccion.ejecutar([ObservacionVisual("Mancha", True, 2)])
        assert len(muestra.defectos) == 1


# --- Nombres técnicos ---

class TestNombreTecnico:
    @pytest.mark.parametrize("texto", ["ISO 9001", "Tornillos M8", "Calibre 0.01", "IRAM-ISO/IEC"])
    def test_validos(self, texto):
        assert validar_nombre_tecnico(texto) == texto

    @pytest.mark.parametrize("texto", ["", "   ", None, "ISO@9001", "Tuercas#"])
    def test_invalidos(self, texto):
        with pytest.raises(DatosInvalidosError):
            validar_nombre_tecnico(texto)

    def test_entidades_aceptan_nombres_tecnicos(self):
        cert = Certificacion("ISO 9001", date(2025, 1, 1), date(2025, 12, 31))
        lote = Lote("Tornillos M8", 100)
        equipo = Equipo("Calibre 0.01", FECHA)
        proc = ProcedimientoVisual(
            limite_gravedad_acumulada=5,
            categoria_equipo_requerida="Calibre 0.01",
            certificacion_requerida="ISO 9001",
        )
        assert cert.nombre == "ISO 9001"
        assert lote.nombre_componentes == "Tornillos M8"
        assert equipo.es_compatible(proc.categoria_equipo_requerida)

    def test_nombre_de_persona_sigue_siendo_solo_letras(self):
        with pytest.raises(DatosInvalidosError):
            Profesional("Ana 2")


# --- Cierre consistente de la inspección ---

class TestCierreConsistente:
    def test_si_falla_el_cierre_de_la_muestra_la_inspeccion_sigue_abierta(self, monkeypatch):
        inspeccion, muestra = _inspeccion_visual(
            ProcedimientoVisual(limite_gravedad_acumulada=5)
        )

        def cierre_que_falla(limite):
            raise RuntimeError("falla simulada al cerrar la muestra")

        monkeypatch.setattr(muestra, "cerrar", cierre_que_falla)

        with pytest.raises(RuntimeError):
            inspeccion.cerrar()
        assert inspeccion.cerrada is False
        assert muestra.estado == EstadoMuestra.EN_INSPECCION

    def test_cierre_normal_marca_cerrada(self):
        inspeccion, muestra = _inspeccion_visual(
            ProcedimientoVisual(limite_gravedad_acumulada=5)
        )
        inspeccion.cerrar()
        assert inspeccion.cerrada is True
        assert muestra.estado == EstadoMuestra.CONFORME
