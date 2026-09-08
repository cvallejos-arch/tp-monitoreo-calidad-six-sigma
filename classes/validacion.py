from datetime import datetime

def validar_entero(numero):
    return isinstance(numero, int)

def validar_cantidad(cantidad):
    validar_entero(cantidad)
    return (cantidad >= 0)

def validar_fecha(fecha_str, formato="%d/%m/%Y"):
    try:
        # Intenta parsear la cadena usando el formato especificado
        fecha_obj = datetime.strptime(fecha_str, formato)
        return True
    except ValueError:
        # Si el formato o la fecha son inválidos
        return False

def validar_rango_fechas(fecha_inicio, fecha_fin):
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")

def validar_texto(texto):
    if not isinstance(texto, str) or texto.strip() == "":
        raise ValueError("El texto no puede estar vacío")

    if not texto.replace(" ", "").isalpha():
        raise ValueError("El texto solo puede contener letras")