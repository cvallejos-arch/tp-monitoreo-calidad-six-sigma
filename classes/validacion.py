from datetime import datetime

def validar_entero(numero):
    return isinstance(numero, int)

def validar_cantidad(cantidad):
    validar_entero(cantidad)
    return (cantidad > 0)

def validar_fecha(fecha_str, formato="%d/%m/%Y"):
    try:
        # Intenta parsear la cadena usando el formato especificado
        fecha_obj = datetime.strptime(fecha_str, formato)
        return True
    except ValueError:
        # Si el formato o la fecha son inválidos
        return False

print(validar_fecha('11/21/2024'))

def validar_texto(texto, nombre_campo):
    if not isinstance(texto, str) or texto.strip() == "":
        raise ValueError(f"{nombre_campo} no puede estar vacío")


def validar_rango_fechas(fecha_inicio, fecha_fin):
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")