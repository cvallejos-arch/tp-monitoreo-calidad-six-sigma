def validar_entero(numero):
    return isinstance(numero, int)

def validar_cantidad(cantidad):
    return ()

def validar_fecha(fecha):
    

def validar_texto(texto, nombre_campo):
    if not isinstance(texto, str) or texto.strip() == "":
        raise ValueError(f"{nombre_campo} no puede estar vacío")