from datetime import datetime

def validar_entero(numero):
    if not isinstance(numero, int):
        raise ValueError(f'{numero} debe ser un entero.')

def validar_cantidad(cantidad):
    validar_entero(cantidad)
    if not (cantidad >= 0):
        raise ValueError(f'{cantidad} debe ser >= 0.')

def validar_fecha(fecha_str, formato="%d/%m/%Y"):
    if not datetime.strptime(fecha_str, formato):
        raise ValueError(f'{fecha_str} debe ser fecha en formato {formato}.')

def validar_rango_fechas(fecha_inicio, fecha_fin):
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")

def validar_gravedad(gravedad):
    validar_entero(gravedad)
    if not (1 <= gravedad <= 5):
        raise ValueError(f'{gravedad} debe estar entre 1 y 5.')

def validar_descripcion(descripcion):
    if not isinstance(descripcion, str) or descripcion.strip() == "":
        raise ValueError("La descripción no puede estar vacía")

def validar_texto(texto):
    if not isinstance(texto, str) or texto.strip() == "":
        raise ValueError("El texto no puede estar vacío")

    if not texto.replace(" ", "").isalpha():
        raise ValueError("El texto solo puede contener letras")

def validar_rango_entero(valor, min_val, max_val, nombre_campo):

    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ValueError(f"El valor de '{nombre_campo}' debe ser un número entero, recibido: {valor}")
    if valor < min_val or valor > max_val:
        raise ValueError(
            f"El valor de '{nombre_campo}' debe estar entre {min_val} y {max_val}, recibido: {valor}"
        )
    return valor