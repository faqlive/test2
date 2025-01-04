import os

def clear_console():
    """
    Función para limpiar la consola
    """
    if os.name == "posix":
        clear = "clear"       
    elif os.name == "ce" or os.name == "nt" or os.name == "dos":
        clear = "cls"

    os.system(clear)