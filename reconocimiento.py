import face_recognition
import cv2
import os

RUTA_USUARIOS = "usuarios"

def reconocer_usuario(cap):
    ret, frame = cap.read()
    if not ret:
        return False, 0.0, None

    #convertir el frame de la cámara a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #detecta y codificar rostros en el frame actual
    rostros_frame = face_recognition.face_locations(frame_rgb)
    codigos_frame = face_recognition.face_encodings(frame_rgb, rostros_frame)

    if not codigos_frame:
        return False, 0.0, None

    #itera sobre los archivos .data en la carpeta usuarios
    for archivo in os.listdir(RUTA_USUARIOS):
        if archivo.endswith(".data"):
            ruta_imagen = os.path.join(RUTA_USUARIOS, archivo)
            try:
                imagen_usuario = face_recognition.load_image_file(ruta_imagen)
                codigos_usuario = face_recognition.face_encodings(imagen_usuario)
                
                if not codigos_usuario:
                    continue  #saltar si no se detectó rostro en esa imagen

                codigo_usuario = codigos_usuario[0]

                for codigo_detectado in codigos_frame:
                    resultado = face_recognition.compare_faces([codigo_usuario], codigo_detectado, tolerance=0.5)
                    distancia = face_recognition.face_distance([codigo_usuario], codigo_detectado)[0]
                    confianza = (1 - distancia) * 100

                    if resultado[0]:
                        usuario_id = os.path.splitext(archivo)[0]  #como por ejemplo: USER001
                        return True, confianza, usuario_id

            except Exception as e:
                print(f"Error al procesar {archivo}: {e}")

    return False, 0.0, None
