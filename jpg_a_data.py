import os

def renombrar_imagenes_a_data():
    carpeta = "usuarios"
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".jpg") or archivo.endswith(".png"):
            ruta_actual = os.path.join(carpeta, archivo)
            nuevo_nombre = os.path.splitext(archivo)[0] + ".data"
            nueva_ruta = os.path.join(carpeta, nuevo_nombre)
            os.rename(ruta_actual, nueva_ruta)
            print(f"Renombrado: {archivo} -> {nuevo_nombre}")

renombrar_imagenes_a_data()