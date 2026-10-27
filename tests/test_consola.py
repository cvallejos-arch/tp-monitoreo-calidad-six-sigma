"""Tests del menú por consola (consola.py). Las respuestas del usuario se simulan
reemplazando input() con monkeypatch: cada llamada a input() devuelve la siguiente
respuesta de la lista."""
import builtins
import pytest
from datetime import date

import consola
from classes.empresa import Empresa
from classes.estado_muestra import EstadoMuestra
from classes.excepciones import DatosInvalidosError, TransicionIlegalError


@pytest.fixture
def respuestas(monkeypatch):
    """Devuelve una función que carga las respuestas que va a 'escribir' el usuario."""
    def cargar(*textos):
        iterador = iter(textos)
        monkeypatch.setattr(builtins, "input", lambda mensaje="": next(iterador))
    return cargar


@pytest.fixture
def empresa_ejemplo(capsys):
    empresa = Empresa()
    consola.cargar_datos_ejemplo(empresa)
    capsys.readouterr()   # descarta lo impreso al cargar
    return empresa


# Con los datos de ejemplo, los números a elegir en cada lista son:
# lotes: 1 = Tornillos M8 | profesionales: 1 = Ana (ISO), 2 = Carlos (sin certificación)
# equipos: 1 = Visual, 2 = Dimensional, 3 = Visual vencido | procedimientos: 1 = Visual, 2 = Dimensional


class TestEntradaDeDatos:
    def test_pedir_texto_repite_si_esta_vacio(self, respuestas):
        respuestas("", "   ", "Ana")
        assert consola.pedir_texto("Nombre") == "Ana"

    def test_pedir_texto_opcional_acepta_vacio(self, respuestas):
        respuestas("")
        assert consola.pedir_texto("Certificación", obligatorio=False) == ""

    def test_pedir_entero_repite_ante_letras_y_fuera_de_rango(self, respuestas, capsys):
        respuestas("dos", "0", "9", "3")
        assert consola.pedir_entero("Número", minimo=1, maximo=5) == 3
        salida = capsys.readouterr().out
        assert "'dos' no es un número entero" in salida
        assert "mayor o igual a 1" in salida
        assert "menor o igual a 5" in salida

    def test_pedir_decimal_acepta_coma(self, respuestas):
        respuestas("abc", "9,5")
        assert consola.pedir_decimal("Valor") == 9.5

    def test_pedir_fecha_repite_ante_formato_invalido(self, respuestas):
        respuestas("15/06/2025", "2025-13-01", "2025-06-15")
        assert consola.pedir_fecha("Fecha") == date(2025, 6, 15)

    def test_pedir_fecha_vacia_es_hoy(self, respuestas):
        respuestas("")
        assert consola.pedir_fecha("Fecha") == date.today()

    def test_pedir_si_no(self, respuestas):
        respuestas("quizas", "S")
        assert consola.pedir_si_no("¿Seguro?") is True

    def test_elegir_de_lista(self, respuestas):
        respuestas("5", "2")
        assert consola.elegir_de_lista("opciones", ["a", "b", "c"], str) == "b"

    def test_elegir_de_lista_vacia_lanza_error(self):
        with pytest.raises(DatosInvalidosError):
            consola.elegir_de_lista("lotes", [], str)


class TestCrearMuestras:
    def test_si_no_entran_todas_no_crea_ninguna(self, respuestas, empresa_ejemplo):
        lote = empresa_ejemplo.listar_lotes()[0]       # 200 unidades, ya usadas por 20 x 10
        nuevo = empresa_ejemplo.crear_registrar_lote("Tuercas", 100)
        respuestas("2", "6", "20")                     # lote 2, 6 muestras de 20 = 120 > 100
        with pytest.raises(TransicionIlegalError):     # lo controla Empresa.crear_registrar_muestras
            consola.crear_muestras(empresa_ejemplo)
        assert len(nuevo.muestras) == 0
        assert len(lote.muestras) == 20

    def test_crea_las_muestras_si_entran(self, respuestas, empresa_ejemplo):
        nuevo = empresa_ejemplo.crear_registrar_lote("Tuercas", 100)
        respuestas("2", "5", "20")
        consola.crear_muestras(empresa_ejemplo)
        assert len(nuevo.muestras) == 5


class TestInspeccionar:
    def test_recorrido_completo_no_conforme(self, respuestas, empresa_ejemplo):
        # lote 1, siguiente de la cola, Ana, equipo visual, proc. visual, hoy,
        # a mano, 1 observación: "Fisura", con defecto, gravedad 5
        respuestas("1", "s", "1", "1", "1", "", "n", "1", "Fisura", "s", "5")
        consola.inspeccionar(empresa_ejemplo)
        muestra = empresa_ejemplo.listar_lotes()[0].muestras[0]
        assert muestra.estado == EstadoMuestra.NO_CONFORME
        assert muestra.reporte is not None

    def test_certificacion_faltante_no_cambia_la_muestra(self, respuestas, empresa_ejemplo,
                                                         capsys):
        # Igual que antes pero con Carlos (2), que no tiene la certificación ISO
        respuestas("1", "s", "2", "1", "1", "", "n", "1", "Fisura", "s", "5")
        empresa = consola.ejecutar_opcion(empresa_ejemplo, "7")
        assert "CertificacionNoVigenteError" in capsys.readouterr().out
        assert empresa is empresa_ejemplo
        muestra = empresa_ejemplo.listar_lotes()[0].muestras[0]
        assert muestra.estado == EstadoMuestra.PENDIENTE
        assert muestra.inspeccion is None

    def test_equipo_vencido(self, respuestas, empresa_ejemplo, capsys):
        respuestas("1", "s", "1", "3", "1", "", "n", "1", "Ok", "n")
        consola.ejecutar_opcion(empresa_ejemplo, "7")
        assert "EquipoNoAptoError" in capsys.readouterr().out

    def test_dato_mal_escrito_no_traba_la_muestra(self, respuestas, empresa_ejemplo):
        """Las observaciones se piden antes de iniciar: escribir mal un dato
        solo hace que se vuelva a preguntar, y la inspección termina bien."""
        respuestas("1", "s", "1", "1", "1", "", "n", "dos", "1", "Rayon", "s", "9", "2")
        consola.inspeccionar(empresa_ejemplo)
        muestra = empresa_ejemplo.listar_lotes()[0].muestras[0]
        assert muestra.estado == EstadoMuestra.CONFORME

    def test_dimensional_con_tolerancias_invertidas_vuelve_a_preguntar(
            self, respuestas, empresa_ejemplo, capsys):
        # proc. dimensional (2) con equipo dimensional (2); primero tolerancias
        # invertidas (10 > 9), después un valor fuera de rango (10.5 en [9, 10])
        respuestas("1", "s", "1", "2", "2", "", "n", "1", "Pieza",
                   "9.5", "10", "9",
                   "10.5", "9", "10")
        consola.inspeccionar(empresa_ejemplo)
        assert "DatosInvalidosError" in capsys.readouterr().out
        muestra = empresa_ejemplo.listar_lotes()[0].muestras[0]
        assert len(muestra.defectos) == 1

    def test_observaciones_al_azar_con_semilla(self, respuestas, empresa_ejemplo):
        respuestas("1", "s", "1", "1", "1", "", "s", "7", "5")
        consola.inspeccionar(empresa_ejemplo)
        muestra = empresa_ejemplo.listar_lotes()[0].muestras[0]
        assert muestra.estado in (EstadoMuestra.CONFORME, EstadoMuestra.NO_CONFORME)

    def test_cola_vacia(self, respuestas, capsys):
        empresa = Empresa()
        empresa.crear_registrar_lote("Vacio", 10)
        respuestas("1", "s")
        consola.ejecutar_opcion(empresa, "7")
        assert "no tiene muestras pendientes" in capsys.readouterr().out


class TestSimulacionYDecision:
    def _simular(self, respuestas, semilla):
        """Carga los datos de ejemplo y simula el lote. Retorna (empresa, lote)."""
        empresa = Empresa()
        consola.cargar_datos_ejemplo(empresa)
        # lote 1, Ana, equipo visual, proc. visual, hoy (los datos de ejemplo se
        # calculan desde hoy), semilla, probabilidad
        respuestas("1", "1", "1", "1", "", str(semilla), "0.15")
        consola.simulacion_aleatoria(empresa)
        return empresa, empresa.listar_lotes()[0]

    def test_misma_semilla_mismo_resultado(self, respuestas):
        _, a = self._simular(respuestas, 5)
        _, b = self._simular(respuestas, 5)
        assert list(map(lambda m: m.estado, a.muestras)) == list(map(lambda m: m.estado, b.muestras))

    def test_semilla_5_aprueba(self, respuestas):
        empresa, lote = self._simular(respuestas, 5)
        assert lote.porcentaje_no_conforme() == 5.0      # exactamente 5 %
        respuestas("1")
        consola.decidir_lote(empresa)
        assert lote.estado.value == "APROBADO"

    def test_semilla_1_rechaza(self, respuestas):
        empresa, lote = self._simular(respuestas, 1)
        assert lote.porcentaje_no_conforme() == 10.0
        respuestas("1")
        consola.decidir_lote(empresa)
        assert lote.estado.value == "RECHAZADO"

    def test_decidir_lote_incompleto(self, respuestas, empresa_ejemplo, capsys):
        respuestas("1")
        consola.ejecutar_opcion(empresa_ejemplo, "9")
        assert "TransicionIlegalError" in capsys.readouterr().out


class TestArchivos:
    def test_guardar_y_cargar_pickle(self, respuestas, empresa_ejemplo, tmp_path):
        ruta = str(tmp_path / "empresa.pkl")
        respuestas("1", ruta)
        consola.archivos(empresa_ejemplo)
        respuestas("2", ruta)
        cargada = consola.ejecutar_opcion(Empresa(), "11")
        assert cargada.resumen() == empresa_ejemplo.resumen()

    def test_archivo_inexistente_no_corta_el_programa(self, respuestas, capsys, tmp_path):
        empresa = Empresa()
        respuestas("2", str(tmp_path / "no_existe.pkl"))
        assert consola.ejecutar_opcion(empresa, "11") is empresa
        assert "Error de archivo" in capsys.readouterr().out


class TestMenuPrincipal:
    def test_opcion_invalida_y_salir(self, respuestas, capsys):
        respuestas("99", "0")
        consola.main()
        salida = capsys.readouterr().out
        assert "Opción inválida" in salida
        assert "Hasta luego." in salida

    def test_ctrl_c_sale_sin_traceback(self, monkeypatch, capsys):
        def interrumpir(mensaje=""):
            raise KeyboardInterrupt
        monkeypatch.setattr(builtins, "input", interrumpir)
        consola.main()
        assert "Hasta luego." in capsys.readouterr().out

    def test_recorrido_cargar_ejemplo_y_ver_lote(self, respuestas, capsys):
        respuestas("12", "8", "1", "0")
        consola.main()
        salida = capsys.readouterr().out
        assert "Datos de ejemplo cargados" in salida
        assert "Capacidad usada: 200/200" in salida


class TestAlertasYReportesPorFecha:
    def test_alertas_de_calibracion(self, respuestas, empresa_ejemplo, capsys):
        # fecha = hoy, avisar a 200 días: entran los dos equipos al día
        respuestas("", "200")
        consola.alertas_calibracion(empresa_ejemplo)
        salida = capsys.readouterr().out
        assert "Equipos VENCIDOS al" in salida and ": 1" in salida
        assert "vencen en los próximos 200 días: 2" in salida
        assert "vence primero" in salida

    def test_reportes_en_orden_de_atencion(self, respuestas, empresa_ejemplo, capsys):
        # Simular el lote con la semilla 1 (2 no conformes) y listar los reportes de hoy
        respuestas("1", "1", "1", "1", "", "1", "0.15")
        consola.simulacion_aleatoria(empresa_ejemplo)
        capsys.readouterr()
        respuestas("", "")
        consola.reportes_por_fecha(empresa_ejemplo)
        salida = capsys.readouterr().out
        assert "2 reporte(s)" in salida
        assert "  1. [" in salida and "  2. [" in salida

    def test_reportes_con_fechas_invertidas(self, respuestas, empresa_ejemplo, capsys):
        respuestas("2025-12-31", "2025-01-01")
        consola.ejecutar_opcion(empresa_ejemplo, "15")
        assert "DatosInvalidosError" in capsys.readouterr().out

    def test_periodo_sin_reportes(self, respuestas, empresa_ejemplo, capsys):
        respuestas("2000-01-01", "2000-12-31")
        consola.reportes_por_fecha(empresa_ejemplo)
        assert "No hay reportes" in capsys.readouterr().out
