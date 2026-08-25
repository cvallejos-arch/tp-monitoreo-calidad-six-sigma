"""
Modelo de dominio: Sistema de Monitoreo de Calidad Industrial.
Version simple: solo clases, __init__ y metodos basicos.
"""

from datetime import date
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
# Defecto
# ---------------------------------------------------------------------------

class Defecto:
    def __init__(self, tipo, descripcion, gravedad):
        self._tipo = tipo
        self._descripcion = descripcion
        self._gravedad = gravedad

    def get_tipo(self):
        return self._tipo

    def get_descripcion(self):
        return self._descripcion

    def get_gravedad(self):
        return self._gravedad

    def es_critico(self):
        pass

    def copia(self):
        pass


# ---------------------------------------------------------------------------
# Certificacion
# ---------------------------------------------------------------------------

class Certificacion:
    def __init__(self, nombre, fecha_inicio, fecha_fin):
        self._nombre = nombre
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin

    def get_nombre(self):
        return self._nombre

    def es_vigente(self, fecha):
        pass


# ---------------------------------------------------------------------------
# Profesional
# ---------------------------------------------------------------------------

class Profesional:
    def __init__(self, id, nombre):
        self._id = id
        self._nombre = nombre
        self._certificaciones = []

    def get_id(self):
        return self._id

    def get_nombre(self):
        return self._nombre

    def agregar_certificacion(self, cert):
        pass

    def tiene_certificacion_vigente(self, nombre, fecha):
        pass


# ---------------------------------------------------------------------------
# Equipo
# ---------------------------------------------------------------------------

class Equipo:
    def __init__(self, id, categoria, fecha_calibracion):
        self._id = id
        self._categoria = categoria
        self._fecha_calibracion = fecha_calibracion

    def get_id(self):
        return self._id

    def get_categoria(self):
        return self._categoria

    def get_fecha_calibracion(self):
        return self._fecha_calibracion

    def esta_calibrado(self, fecha):
        pass

    def es_compatible(self, categoria_requerida):
        pass


# ---------------------------------------------------------------------------
# Procedimiento y variantes polimorficas
# ---------------------------------------------------------------------------

class Procedimiento:
    def __init__(self, id, limite_gravedad_acumulada, categoria_equipo_requerida, certificacion_requerida=None):
        self._id = id
        self._limite_gravedad_acumulada = limite_gravedad_acumulada
        self._categoria_equipo_requerida = categoria_equipo_requerida
        self._certificacion_requerida = certificacion_requerida

    def get_id(self):
        return self._id

    def get_limite_gravedad_acumulada(self):
        return self._limite_gravedad_acumulada

    def get_categoria_equipo_requerida(self):
        return self._categoria_equipo_requerida

    def get_certificacion_requerida(self):
        return self._certificacion_requerida

    def evaluar(self, observaciones):
        pass


class ProcedimientoDimensional(Procedimiento):
    def evaluar(self, observaciones):
        pass


class ProcedimientoVisual(Procedimiento):
    def evaluar(self, observaciones):
        pass


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

class Reporte:
    def __init__(self, muestra_id, lote_id, profesional_id, fecha, defectos):
        self._muestra_id = muestra_id
        self._lote_id = lote_id
        self._profesional_id = profesional_id
        self._fecha = fecha
        self._defectos = defectos

    def get_muestra_id(self):
        return self._muestra_id

    def get_lote_id(self):
        return self._lote_id

    def get_profesional_id(self):
        return self._profesional_id

    def get_fecha(self):
        return self._fecha

    def get_defectos(self):
        return self._defectos


# ---------------------------------------------------------------------------
# Inspeccion
# ---------------------------------------------------------------------------

class Inspeccion:
    def __init__(self, id, muestra, profesional, equipo, procedimiento, fecha):
        self._id = id
        self._muestra = muestra
        self._profesional = profesional
        self._equipo = equipo
        self._procedimiento = procedimiento
        self._fecha = fecha
        self._defectos = []
        self._cerrada = False

    def get_id(self):
        return self._id

    def get_muestra_id(self):
        return self._muestra.get_id()

    def get_profesional_id(self):
        return self._profesional.get_id()

    def get_equipo_id(self):
        return self._equipo.get_id()

    def get_procedimiento_id(self):
        return self._procedimiento.get_id()

    def get_fecha(self):
        return self._fecha

    def get_defectos(self):
        return self._defectos

    def ejecutar(self, observaciones):
        pass

    def cerrar(self):
        pass


# ---------------------------------------------------------------------------
# Muestra
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
# Administrador
# ---------------------------------------------------------------------------

class Administrador:
    def __init__(self):
        self._lotes = {}
        self._muestras = {}
        self._profesionales = {}
        self._equipos = {}
        self._procedimientos = {}
        self._inspecciones = {}

    def registrar_lote(self, id, cantidad):
        pass

    def registrar_muestra(self, id, cantidad):
        pass

    def registrar_profesional(self, id, nombre):
        pass

    def registrar_equipo(self, id, categoria, fecha_calibracion):
        pass

    def registrar_procedimiento(self, proc):
        pass

    def lanzar_inspeccion(self, muestra, profesional, equipo, procedimiento, fecha):
        pass