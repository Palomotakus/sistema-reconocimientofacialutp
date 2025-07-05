import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import csv
from reconocimiento import reconocer_usuario
from logs import guardar_log
from registrar import crear_apartado_registro
from dashboard import DashboardInventario  # Importamos el dashboard
import sqlite3

IMG_PATH = "assets/logo.png"

def cargar_usuarios_desde_db():
    datos = {}
    try:
        conn = sqlite3.connect("mi_base.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, cargo, area, acceso_dashboard FROM usuarios")
        for fila in cursor.fetchall():
            datos[fila[0]] = {
                "nombre": fila[1],
                "apellido": fila[2],
                "cargo": fila[3],
                "area": fila[4],
                "acceso_dashboard": fila[5]
            }
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar la base de datos: {str(e)}")
    return datos

datos_usuarios = cargar_usuarios_desde_db()

# Ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Seguridad Facial")
ventana.attributes("-fullscreen", True)
ventana.configure(bg="#f0f0f0")

# Configurar grid para que se expanda correctamente
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)

# Inicialización optimizada de la cámara
try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise Exception("No se pudo acceder a la cámara")
except Exception as e:
    messagebox.showerror("Error", str(e))
    cap = None

# Sistema de frames
frame_principal = tk.Frame(ventana, bg="#f0f0f0")
frame_registro = tk.Frame(ventana, bg="#f0f0f0")

for frame in (frame_principal, frame_registro):
    frame.grid(row=0, column=0, sticky="nsew")

frame_principal.tkraise()


def ir_a_registro():
    btn_reconocer.config(state="disabled")
    frame_registro.tkraise()
    crear_apartado_registro(frame_registro, frame_principal, cap, datos_usuarios, btn_reconocer)

def configurar_interfaz_principal():
    # Frame principal
    main_frame = tk.Frame(frame_principal, bg="#f0f0f0")
    main_frame.pack(expand=True, fill="both")

    # Logo/Cámara
    frame_imagen = tk.Frame(main_frame, bg="#f0f0f0")
    frame_imagen.pack(pady=20)
    
    label_video = tk.Label(frame_imagen, bg="#f0f0f0")
    label_video.pack()

    # Información
    info_usuario = tk.Label(main_frame, text="", font=("Arial", 16), bg="#f0f0f0", justify='center')
    info_usuario.pack(pady=10)

    # Frame para botones de acción post-reconocimiento
    action_frame = tk.Frame(main_frame, bg="#f0f0f0")
    action_frame.pack(pady=10)

    # Variables de estado
    camera_running = False
    mensaje = None
    btn_acceder = None  # Botón de acceso al dashboard

    def mostrar_logo():
        if os.path.exists(IMG_PATH):
            imagen = Image.open(IMG_PATH)
            imagen = imagen.resize((600, 400), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(imagen)
            label_video.config(image=img_tk)
            label_video.image = img_tk

    def actualizar_video(label):
        if camera_running:
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imagen = Image.fromarray(frame)
                imagen = imagen.resize((600, 400))
                img_tk = ImageTk.PhotoImage(image=imagen)
                label.imgtk = img_tk
                label.configure(image=img_tk)
            ventana.after(10, lambda: actualizar_video(label))

    def reconocer_usuario_button(label, info):
        nonlocal camera_running, mensaje
        camera_running = True
        actualizar_video(label)
        btn_reconocer.config(text="Detener", bg="red", command=lambda: detener_camara(label, info))
        
        mensaje = tk.Label(main_frame, text="", font=("Arial", 20), bg="yellow")
        mensaje.pack(pady=20)
        cuenta_regresiva(5, label, info, mensaje)

    def cuenta_regresiva(segundos, label, info, msg):
        if segundos > 0:
            msg.config(text=f"Quédese quieto, reconocimiento en: {segundos}")
            ventana.after(1000, lambda: cuenta_regresiva(segundos-1, label, info, msg))
        else:
            resultado, confianza, usuario_id = reconocer_usuario(cap)
            if resultado and usuario_id in datos_usuarios:
                datos = datos_usuarios[usuario_id]
                texto = (f"Usuario reconocido con éxito\n\n"
                         f"Nombre: {datos['nombre']} {datos['apellido']}\n"
                         f"Cargo: {datos['cargo']}\n"
                         f"Área: {datos['area']}\n"
                         f"Confianza: {confianza:.2f}%")
                info.config(text=texto, fg="green")
                label.config(bg="green")
                
                # Mostrar botón de Acceder si tiene permiso
                nonlocal btn_acceder
                if btn_acceder:
                    btn_acceder.destroy()
                
                if datos.get('acceso_dashboard', 'NO') == 'SI':
                    btn_acceder = tk.Button(action_frame, text="ACCEDER AL DASHBOARD", 
                                          font=("Arial", 14), bg="#4CAF50", fg="white",
                                          command=lambda: abrir_dashboard(ventana))
                    btn_acceder.pack(pady=10)
                
            else:
                info.config(text="Usuario no reconocido", fg="red")
                label.config(bg="red")
            
            guardar_log(usuario_id, confianza, resultado, datos_usuarios)
            msg.destroy()

    def detener_camara(label, info):
        nonlocal camera_running, btn_acceder
        camera_running = False
        label.config(bg="#f0f0f0")
        info.config(text="")
        if btn_acceder:
            btn_acceder.destroy()
            btn_acceder = None
        btn_reconocer.config(text="Reconocer", bg="#4CAF50", 
                           command=lambda: reconocer_usuario_button(label, info))
        mostrar_logo()

    def abrir_dashboard(root):
        ventana_dashboard = tk.Toplevel(root)
        ventana_dashboard.attributes("-fullscreen", True)
        app = DashboardInventario(
            ventana_dashboard,
            on_cerrar=ventana_dashboard.destroy,
            on_detener=lambda: detener_camara(label_video, info_usuario)
        )


    # Botón de reconocimiento
    btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
    btn_frame.pack(pady=20)

    btn_reconocer = tk.Button(btn_frame, text="Reconocer", font=("Arial", 16), bg="#4CAF50", fg="white",
                             width=20, height=2, command=lambda: reconocer_usuario_button(label_video, info_usuario))
    btn_reconocer.pack()

    # Botones inferiores
    bottom_frame = tk.Frame(frame_principal, bg="#f0f0f0")
    bottom_frame.pack(side='bottom', fill='x', pady=10)
    
    tk.Button(bottom_frame, text="Registrar", font=("Arial", 12), bg="#2196F3", fg="white",
             width=12, command=ir_a_registro).pack(side='right', padx=20)
    
    tk.Button(bottom_frame, text="Salir", font=("Arial", 10), command=ventana.destroy).pack(side='left', padx=20)

    mostrar_logo()
    return label_video, info_usuario, btn_reconocer

label_video, info_usuario, btn_reconocer = configurar_interfaz_principal()
ventana.mainloop()

if cap is not None:
    cap.release()