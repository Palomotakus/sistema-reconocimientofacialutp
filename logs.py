import os
import sqlite3
from datetime import datetime

DB_PATH = "mi_base.db"
LOG_PATH = "logs"  # opcional, para guardar txt también

def guardar_log(usuario_id=None, confianza=0, exito=False, datos_usuarios=None):
    """
    Guarda un log en la base de datos SQLite.
    
    Parámetros:
        usuario_id (str): ID del usuario reconocido.
        confianza (float): Porcentaje de confianza del reconocimiento.
        exito (bool): Si el reconocimiento fue exitoso o no.
        datos_usuarios (dict): Diccionario con los datos de los usuarios (puede ser None si no se usa).
    """

    ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Asegura que el ID no sea None para guardar
    usuario_final = usuario_id if usuario_id else "DESCONOCIDO"
    estado = "RECONOCIDO" if exito else "NO RECONOCIDO"

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (ahora, usuario_final, estado, confianza))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error al guardar log en DB: {e}")

    # (opcional) guardar .txt también
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    nombre_archivo = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    ruta_completa = os.path.join(LOG_PATH, nombre_archivo)

    with open(ruta_completa, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Fecha y hora: {ahora}\n")

        if exito and datos_usuarios and usuario_id in datos_usuarios:
            datos = datos_usuarios[usuario_id]
            log_file.write("Acceso concedido\n")
            log_file.write(f"ID: {usuario_id}\n")
            log_file.write(f"Nombre: {datos['nombre']}\n")
            log_file.write(f"Cargo: {datos['cargo']}\n")
            log_file.write(f"Confianza: {confianza:.2f}%\n")
        else:
            log_file.write("Acceso denegado\n")
            log_file.write(f"Confianza detectada: {confianza:.2f}%\n")
