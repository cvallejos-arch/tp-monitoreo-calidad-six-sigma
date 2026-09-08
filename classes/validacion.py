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

def validar_texto(texto):
    if not isinstance(texto, str) or texto.strip() == "":
        raise ValueError("El texto no puede estar vacío")

    if not texto.replace(" ", "").isalpha():
        raise ValueError("El texto solo puede contener letras")