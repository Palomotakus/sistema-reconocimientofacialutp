import face_recognition
import cv2
from tkinter import messagebox
import os

DNI_PATH = "assets/dni.jpg" #de aqui saca el dni

def reconocer_usuario(cap):
    ret, frame = cap.read()  #agarra el frame de la camara pa comparar
    if not ret:
        messagebox.showerror("Error", "No se pudo capturar la imagen")
        return False
    
    #convertir a imagen a rgb por problema que hubo en main.py tmr
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #tambien convertir la imagen del dni a rgb por el problema de main.py x2
    dni_image = face_recognition.load_image_file(DNI_PATH)
    dni_encoding = face_recognition.face_encodings(dni_image)[0]  # Codificación de la cara en el DNI
    
    #primero ve si hay un rostro reconocible en la imagen
    faces_in_frame = face_recognition.face_locations(frame_rgb)
    encodings_in_frame = face_recognition.face_encodings(frame_rgb, faces_in_frame)
    
    #compara la cara reconocida con la del dni
    for encoding in encodings_in_frame:
        matches = face_recognition.compare_faces([dni_encoding], encoding, tolerance=0.5) #esta vaina es la tolerancia, de momento en 0.4 manda error a cada rato y en 0.5 da muchos positivos, hay que jguar entre esso numero
        if True in matches:
            return True  #Si se reconocio piola

    return False  #no se reconocio
