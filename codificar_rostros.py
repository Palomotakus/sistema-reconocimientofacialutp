import face_recognition
import os
import pickle

def generar_encodings():
    path = "usuarios"
    codificados = {}

    for archivo in os.listdir(path):
        if archivo.endswith(".data"):
            id_usuario = os.path.splitext(archivo)[0]
            ruta = os.path.join(path, archivo)
            imagen = face_recognition.load_image_file(ruta)
            encoding = face_recognition.face_encodings(imagen)

            if encoding:
                codificados[id_usuario] = encoding[0]

    with open("encodings.pkl", "wb") as f:
        pickle.dump(codificados, f)

if __name__ == "__main__":
    generar_encodings()
    print("Encodings generados.")
