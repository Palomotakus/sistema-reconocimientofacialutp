import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from reconocimiento import reconocer_usuario 

IMG_PATH = "assets/logo.png"

#ventana general
ventana = tk.Tk()
ventana.title("Sistema de Seguridad Facial")
ventana.attributes("-fullscreen", True)
ventana.configure(bg="#f0f0f0")

#el contenedor del logo y donde tambien la camara
frame_imagen = tk.Frame(ventana, bg="#f0f0f0") #se pone dentro de la ventana general
frame_imagen.pack(pady=50)

# Label donde irá la imagen o la cámara
label_video = tk.Label(frame_imagen, bg="#f0f0f0") # se ingresa dentro del frame_imagen
label_video.pack()

#control de camara
cap = None
camera_running = False

#funcion del logo y error por si no la encuentra
def mostrar_logo():
    if os.path.exists(IMG_PATH):
        imagen = Image.open(IMG_PATH)
        imagen = imagen.resize((600, 400), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(imagen)
        label_video.config(image=img_tk)
        label_video.image = img_tk
    else:
        label_video.config(text="(imagen no encontrada)", font=("Arial", 12), bg="#f0f0f0")

#funcion para encender la camara y mostrarla en el label y su funcion error por si falla
def mostrar_camara():
    global cap, camera_running
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara")
        return

    camera_running = True
    actualizar_video()


#actualizacion constante de la camara para verse a uno mismo
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

#detener la camara y regresar al logoo
def detener_camara():
    global cap, camera_running, mensaje
    camera_running = False
    if cap:
        cap.release()

    label_video.config(bg="#f0f0f0")

    if mensaje and mensaje.winfo_exists():
        mensaje.destroy()

    #en caso se utilice el boton DETENER se restaura el boton RECONOCER
    btn_reconocer.config(text="Reconocer", bg="#4CAF50", command=reconocer_usuario_button)

    mostrar_logo()

#BOTON RECONOCER pa reconocer p, ya no se porque pongo tantos comentarios fwmfirtfgdsgv
def reconocer_usuario_button():
    global mensaje
    mostrar_camara()

    #en caso se utilice el boton RECONOCER lo cambia por el de DETENER, para evitar un bug de ciclo que bloquea la camara tmr
    btn_reconocer.config(text="Detener", bg="red", command=detener_camara)

    #se crea la cuenta regresiva en amarillo para que te puedas acomodar, la foto se toma al final del a cuenta regresiva
    mensaje = tk.Label(ventana, text="", font=("Arial", 20), bg="yellow")
    mensaje.place(relx=0.5, rely=0.8, anchor="center")

    cuenta_regresiva(5)

def cuenta_regresiva(segundos):
    global mensaje
    if segundos > 0:
        mensaje.config(text=f"Quédese quieto, reconocimiento en: {segundos}")
        ventana.after(1000, cuenta_regresiva, segundos - 1)
    else:
        #una vez terminado la cuenta regresiva recien toma la foto para reconocer
        if reconocer_usuario(cap):
            messagebox.showinfo("Reconocido", "¡Cara reconocida!", icon="info")
            label_video.config(bg="green")
        else:
            messagebox.showinfo("No Reconocido", "No se pudo reconocer la cara.", icon="error")
            label_video.config(bg="red")

#BOTONES Y SUS FUNCIONES ACTIVAS ASI COMO SUS FORMAS
#BOTON PA RECONOCER
btn_reconocer = tk.Button(ventana, text="Reconocer", font=("Arial", 16), bg="#4CAF50", fg="white",
                          width=20, height=2, command=reconocer_usuario_button)
btn_reconocer.pack(pady=10)

#EL BOTON PA REGISTRAR
btn_registrar = tk.Button(ventana, text="Registrar", font=("Arial", 12), bg="#2196F3", fg="white",
                          width=12)
btn_registrar.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

#BOTON PARA SALIR DE LA APP (ESTE NO ESTARA EN LA ENTREGA DE LA APLICACION PUES ESTE DEBERIA ESTAR EN UNA TERMINAL)
#EL BOTON SALIR ES PARA ESTAR MAS COMODO AL SALIR DE LA APP DE MOMENTO
btn_salir = tk.Button(ventana, text="Salir", font=("Arial", 10), command=ventana.destroy)
btn_salir.place(relx=0.0, rely=1.0, anchor="sw", x=20, y=-20)

#el logo de muestra por defecto
mostrar_logo()

ventana.mainloop()
