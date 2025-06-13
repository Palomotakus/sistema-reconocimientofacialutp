import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import csv
from reconocimiento import reconocer_usuario

IMG_PATH = "assets/logo.png"
CSV_PATH = "usuarios.csv"

# Cargar datos desde el CSV
datos_usuarios = {}
if os.path.exists(CSV_PATH):
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            datos_usuarios[fila["id"]] = {
                "nombre": fila["nombre"],
                "cargo": fila["cargo"],
                "edad": fila["edad"]
            }

# Ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Seguridad Facial")
ventana.attributes("-fullscreen", True)
ventana.configure(bg="#f0f0f0")

# Frame donde va la cámara o imagen
frame_imagen = tk.Frame(ventana, bg="#f0f0f0")
frame_imagen.pack(pady=50)

label_video = tk.Label(frame_imagen, bg="#f0f0f0")
label_video.pack()

# Texto informativo debajo de la cámara
info_usuario = tk.Label(ventana, text="", font=("Arial", 16), bg="#f0f0f0")
info_usuario.pack()

# Control de cámara
cap = None
camera_running = False
mensaje = None

def mostrar_logo():
    if os.path.exists(IMG_PATH):
        imagen = Image.open(IMG_PATH)
        imagen = imagen.resize((600, 400), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(imagen)
        label_video.config(image=img_tk)
        label_video.image = img_tk
    else:
        label_video.config(text="(imagen no encontrada)", font=("Arial", 12), bg="#f0f0f0")

def mostrar_camara():
    global cap, camera_running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara")
        return
    camera_running = True
    actualizar_video()

def actualizar_video():
    global cap, camera_running
    if camera_running:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame)
            imagen = imagen.resize((600, 400))
            img_tk = ImageTk.PhotoImage(image=imagen)
            label_video.imgtk = img_tk
            label_video.configure(image=img_tk)
        ventana.after(10, actualizar_video)

def detener_camara():
    global cap, camera_running, mensaje
    camera_running = False
    if cap:
        cap.release()

    label_video.config(bg="#f0f0f0")
    info_usuario.config(text="", fg="black")

    if mensaje and mensaje.winfo_exists():
        mensaje.destroy()

    btn_reconocer.config(text="Reconocer", bg="#4CAF50", command=reconocer_usuario_button)
    mostrar_logo()

def reconocer_usuario_button():
    global mensaje
    mostrar_camara()

    btn_reconocer.config(text="Detener", bg="red", command=detener_camara)

    mensaje = tk.Label(ventana, text="", font=("Arial", 20), bg="yellow")
    mensaje.place(relx=0.5, rely=0.8, anchor="center")

    cuenta_regresiva(5)

def cuenta_regresiva(segundos):
    global mensaje
    if segundos > 0:
        mensaje.config(text=f"Quédese quieto, reconocimiento en: {segundos}")
        ventana.after(1000, cuenta_regresiva, segundos - 1)
    else:
        resultado, confianza, usuario_id = reconocer_usuario(cap)

        #si fue reconocido
        if resultado and usuario_id in datos_usuarios:
            datos = datos_usuarios[usuario_id]
            texto = (f"Usuario reconocido con éxito\n\n"
                     f"Nombre: {datos['nombre']}\n"
                     f"Cargo: {datos['cargo']}\n"
                     f"Edad: {datos['edad']} años\n"
                     f"Confianza: {confianza:.2f}%")
            info_usuario.config(text=texto, fg="green")
            label_video.config(bg="green")

        #si no reconocido
        else:
            info_usuario.config(text="Usuario no reconocido", fg="red")
            label_video.config(bg="red")

        #eliminar mensaje amarillo
        if mensaje and mensaje.winfo_exists():
            mensaje.destroy()


# Botones
btn_reconocer = tk.Button(ventana, text="Reconocer", font=("Arial", 16), bg="#4CAF50", fg="white",
                          width=20, height=2, command=reconocer_usuario_button)
btn_reconocer.pack(pady=10)

btn_registrar = tk.Button(ventana, text="Registrar", font=("Arial", 12), bg="#2196F3", fg="white",
                          width=12)
btn_registrar.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

btn_salir = tk.Button(ventana, text="Salir", font=("Arial", 10), command=ventana.destroy)
btn_salir.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)

mostrar_logo()
ventana.mainloop()
