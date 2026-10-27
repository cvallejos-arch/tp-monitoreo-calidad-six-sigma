"""Tests de Empresa: filtrado genérico del registro (filter + lambda sobre dict)
y resumen del registro (recorrido de diccionario)."""
import pytest
from datetime import date

from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.proc_dimensional import ProcedimientoDimensional
from classes.estado_lote import EstadoLote
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError, TransicionIlegalError


@pytest.fixture
def empresa_con_lotes():
    empresa = Empresa()
    empresa.crear_registrar_lote("Tornillos", 100)
    empresa.crear_registrar_lote("Tuercas", 100)
    empresa.crear_registrar_lote("Tornillos", 500)
    return empresa


class TestFiltrar:
    def test_sin_filtros_retorna_todo(self, empresa_con_lotes):
        assert len(empresa_con_lotes.listar_lotes()) == 3

    def test_retorna_lista(self, empresa_con_lotes):
        assert isinstance(empresa_con_lotes.listar_lotes(), list)

    def test_un_filtro(self, empresa_con_lotes):
        res = empresa_con_lotes.listar_lotes(nombre_componentes="Tornillos")
        assert len(res) == 2

    def test_varios_filtros_deben_cumplirse_todos(self, empresa_con_lotes):
        res = empresa_con_lotes.listar_lotes(
            nombre_componentes="Tornillos", cantidad_fabricada=500
        )
        assert len(res) == 1
        assert res[0].cantidad_fabricada == 500

    def test_filtro_sin_coincidencias(self, empresa_con_lotes):
        assert empresa_con_lotes.listar_lotes(estado=EstadoLote.APROBADO) == []

    def test_atributo_inexistente_lanza_error(self, empresa_con_lotes):
        with pytest.raises(DatosInvalidosError) as exc:
            empresa_con_lotes.listar_lotes(estdo=EstadoLote.APROBADO)
        assert exc.value.detalles["atributo"] == "estdo"

    def test_atributo_inexistente_en_registro_vacio_tambien_falla(self):
        """La validación usa la clase, no los objetos: falla aunque no haya datos."""
        with pytest.raises(DatosInvalidosError):
            Empresa().listar_muestras(color="rojo")

    def test_filtrar_muestras_por_estado(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Arandelas", 100)
        m1 = empresa.crear_registrar_muestra(10, lote)
        empresa.crear_registrar_muestra(10, lote)
        m1.iniciar_inspeccion()
        assert empresa.listar_muestras(estado=EstadoMuestra.EN_INSPECCION) == [m1]
        assert len(empresa.listar_muestras(estado=EstadoMuestra.PENDIENTE)) == 1


    def test_filtrar_inspecciones_por_cerrada(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Arandelas", 100)
        muestra = empresa.crear_registrar_muestra(10, lote)
        prof = empresa.crear_registrar_profesional("Laura")
        prof.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
        equipo = empresa.crear_registrar_equipo("Visual", date(2025, 5, 1))
        proc = empresa.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5)
        insp = empresa.lanzar_inspeccion(muestra, prof, equipo, proc, date(2025, 6, 1))

        assert empresa.listar_inspecciones(cerrada=False) == [insp]
        assert empresa.listar_inspecciones(cerrada=True) == []

        insp.cerrar()
        assert empresa.listar_inspecciones(cerrada=True) == [insp]
        assert empresa.listar_inspecciones(cerrada=False) == []


class TestListarProfesionalesEquiposProcedimientos:
    """Métodos públicos que usa la interfaz para no acceder a empresa._registros."""

    def test_listar_profesionales(self):
        empresa = Empresa()
        ana = empresa.crear_registrar_profesional("Ana")
        carlos = empresa.crear_registrar_profesional("Carlos")
        assert empresa.listar_profesionales() == [ana, carlos]
        assert empresa.listar_profesionales(nombre="Ana") == [ana]

    def test_listar_equipos_por_categoria(self):
        empresa = Empresa()
        visual = empresa.crear_registrar_equipo("Visual", date(2025, 6, 1))
        dimensional = empresa.crear_registrar_equipo("Dimensional", date(2025, 6, 1))
        assert empresa.listar_equipos() == [visual, dimensional]
        assert empresa.listar_equipos(categoria="Dimensional") == [dimensional]

    def test_listar_procedimientos(self):
        empresa = Empresa()
        visual = empresa.crear_registrar_procedimiento(
            ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")
        dimensional = empresa.crear_registrar_procedimiento(
            ProcedimientoDimensional, limite_gravedad_acumulada=10)
        assert empresa.listar_procedimientos() == [visual, dimensional]
        assert empresa.listar_procedimientos(certificacion_requerida="ISO") == [visual]

    def test_listas_vacias_en_empresa_nueva(self):
        empresa = Empresa()
        assert empresa.listar_profesionales() == []
        assert empresa.listar_equipos() == []
        assert empresa.listar_procedimientos() == []

    def test_retorna_lista_nueva(self):
        """Modificar la lista devuelta no cambia el registro de la empresa."""
        empresa = Empresa()
        empresa.crear_registrar_profesional("Ana")
        empresa.listar_profesionales().clear()
        assert len(empresa.listar_profesionales()) == 1

    def test_filtro_inexistente_lanza_error(self):
        with pytest.raises(DatosInvalidosError):
            Empresa().listar_equipos(color="rojo")


class TestResumen:
    def test_resumen_empresa_vacia(self):
        assert Empresa().resumen() == {
            "lotes": 0,
            "muestras": 0,
            "profesionales": 0,
            "equipos": 0,
            "procedimientos": 0,
            "inspecciones": 0,
        }

    def test_resumen_cuenta_cada_categoria(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        empresa.crear_registrar_muestra(10, lote)
        empresa.crear_registrar_muestra(10, lote)
        empresa.crear_registrar_profesional("Ana")
        empresa.crear_registrar_equipo("Visual", date(2025, 6, 1))

        resumen = empresa.resumen()

        assert resumen["lotes"] == 1
        assert resumen["muestras"] == 2
        assert resumen["profesionales"] == 1
        assert resumen["equipos"] == 1
        assert resumen["procedimientos"] == 0
        assert resumen["inspecciones"] == 0


class TestCrearVariasMuestras:
    """crear_registrar_muestras(lote, *cantidades): *args."""

    def test_crea_una_muestra_por_argumento(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        muestras = empresa.crear_registrar_muestras(lote, 50, 30, 20)
        assert isinstance(muestras, tuple)
        assert list(map(lambda m: m.cantidad, muestras)) == [50, 30, 20]
        assert all(map(lambda m: m in lote, muestras))
        assert len(empresa.listar_muestras()) == 3

    def test_desempaquetar_una_lista(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        assert len(empresa.crear_registrar_muestras(lote, *[10] * 10)) == 10
        assert lote.capacidad_libre == 0

    def test_si_no_entran_todas_no_crea_ninguna(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        with pytest.raises(TransicionIlegalError):
            empresa.crear_registrar_muestras(lote, 60, 60)
        assert len(lote.muestras) == 0
        assert empresa.listar_muestras() == []

    def test_una_cantidad_invalida_no_crea_ninguna(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        with pytest.raises(DatosInvalidosError):
            empresa.crear_registrar_muestras(lote, 10, 0, 10)
        assert len(lote.muestras) == 0

    def test_sin_cantidades(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        with pytest.raises(DatosInvalidosError):
            empresa.crear_registrar_muestras(lote)

    def test_respetan_el_orden_de_la_cola(self):
        empresa = Empresa()
        lote = empresa.crear_registrar_lote("Tornillos", 100)
        primera, segunda = empresa.crear_registrar_muestras(lote, 10, 20)
        assert lote.siguiente_muestra_pendiente() is primera
