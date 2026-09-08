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

