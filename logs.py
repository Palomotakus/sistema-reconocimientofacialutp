import os
from datetime import datetime

# Carpeta donde se guardarán los logs
LOG_PATH = "logs"

def guardar_log(usuario_id=None, confianza=0, exito=False, datos_usuarios=None):
    """
    Guarda un log en formato .txt con la información del acceso (permitido o denegado).
    
    Parámetros:
        usuario_id (str): ID del usuario reconocido.
        confianza (float): Porcentaje de confianza del reconocimiento.
        exito (bool): Si el reconocimiento fue exitoso o no.
        datos_usuarios (dict): Diccionario con los datos de los usuarios.
    """

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    ahora = datetime.now()
    nombre_archivo = f"log_{ahora.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    ruta_completa = os.path.join(LOG_PATH, nombre_archivo)

    with open(ruta_completa, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Fecha y hora: {ahora.strftime('%Y-%m-%d %H:%M:%S')}\n")

        if exito and usuario_id in datos_usuarios:
            datos = datos_usuarios[usuario_id]
            log_file.write("Acceso concedido\n")
            log_file.write(f"ID: {usuario_id}\n")
            log_file.write(f"Nombre: {datos['nombre']}\n")
            log_file.write(f"Cargo: {datos['cargo']}\n")
            log_file.write(f"Edad: {datos['edad']}\n")
            log_file.write(f"Confianza: {confianza:.2f}%\n")
        else:
            log_file.write("Acceso denegado\n")
            log_file.write(f"Confianza detectada: {confianza:.2f}%\n")
