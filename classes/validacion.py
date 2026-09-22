from datetime import date
from classes.excepciones import DatosInvalidosError


def validar_entero(valor, nombre_campo="valor"):
    """Valida que el valor sea un entero (no bool). Retorna el valor validado."""
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe ser un entero, recibido: {valor}"
        )
    return valor


def validar_cantidad(cantidad):
    """Valida que la cantidad sea un entero estrictamente positivo (> 0).
    Retorna el valor validado."""
    validar_entero(cantidad, "cantidad")
    if cantidad <= 0:
        raise DatosInvalidosError(
            f"La cantidad debe ser un entero positivo (> 0), recibido: {cantidad}"
        )
    return cantidad


def validar_gravedad(gravedad):
    """Valida que la gravedad sea un entero entre 1 y 5 inclusive.
    Retorna el valor validado."""
    validar_entero(gravedad, "gravedad")
    if not (1 <= gravedad <= 5):
        raise DatosInvalidosError(
            f"La gravedad debe estar entre 1 y 5, recibido: {gravedad}"
        )
    return gravedad


def validar_texto(texto, nombre_campo="texto"):
    """Valida que el texto sea un string no vacío.
    Solo permite letras y espacios. Retorna el valor validado."""
    if not isinstance(texto, str) or texto.strip() == "":
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' no puede estar vacío"
        )
    if not texto.replace(" ", "").isalpha():
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' solo puede contener letras, recibido: '{texto}'"
        )
    return texto


def validar_descripcion(descripcion):
    """Valida que la descripción sea un string no vacío.
    Permite cualquier carácter. Retorna el valor validado."""
    if not isinstance(descripcion, str) or descripcion.strip() == "":
        raise DatosInvalidosError("La descripción no puede estar vacía")
    return descripcion


def validar_rango_fechas(fecha_inicio, fecha_fin):
    """Valida que fecha_inicio <= fecha_fin. Ambas deben ser instancias de date."""
    validar_fecha_tipo(fecha_inicio, "fecha_inicio")
    validar_fecha_tipo(fecha_fin, "fecha_fin")
    if fecha_inicio > fecha_fin:
        raise DatosInvalidosError(
            "La fecha de inicio no puede ser posterior a la fecha de fin"
        )


def validar_fecha_tipo(fecha, nombre_campo="fecha"):
    """Valida que el valor sea una instancia de date. Retorna el valor validado."""
    if not isinstance(fecha, date):
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe ser de tipo date, recibido: {type(fecha).__name__}"
        )
    return fecha


def validar_rango_entero(valor, min_val, max_val, nombre_campo="valor"):
    """Valida que el valor sea un entero dentro del rango [min_val, max_val].
    Retorna el valor validado."""
    validar_entero(valor, nombre_campo)
    if valor < min_val or valor > max_val:
        raise DatosInvalidosError(
            f"El campo '{nombre_campo}' debe estar entre {min_val} y {max_val}, recibido: {valor}"
        )
    return valor