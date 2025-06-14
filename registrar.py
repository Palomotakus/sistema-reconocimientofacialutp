import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import csv
import os
from datetime import datetime
import subprocess

USUARIOS_CSV = "usuarios.csv"
CARPETA_USUARIOS = "usuarios"

# ================= Función para obtener nuevo ID automático =================
def generar_nuevo_id():
    if not os.path.exists(USUARIOS_CSV):
        return "USER001"
    with open(USUARIOS_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ids = [int(row['ID'].replace("USER", "")) for row in reader if row['ID'].startswith("USER")]
        nuevo_id = max(ids) + 1 if ids else 1
        return f"USER{nuevo_id:03d}"


# =================== Mostrar apartado de registro ===========================
def mostrar_apartado_registro(root, frame_contenido, label_video, info_usuario, btn_reconocer):
    for widget in frame_contenido.winfo_children():
        widget.destroy()

    # Variables
    id_auto = generar_nuevo_id()
    var_nombre = tk.StringVar()
    var_apellido = tk.StringVar()
    var_cargo = tk.StringVar()
    var_area = tk.StringVar()
    foto_tomada = [None]  # para mutabilidad dentro de funciones

    tk.Label(frame_contenido, text=f"ID asignado: {id_auto}", font=("Arial", 12)).pack(pady=5)
    tk.Entry(frame_contenido, textvariable=var_nombre, width=30).pack(pady=5)
    tk.Label(frame_contenido, text="Nombre").pack()

    tk.Entry(frame_contenido, textvariable=var_apellido, width=30).pack(pady=5)
    tk.Label(frame_contenido, text="Apellido").pack()

    opciones_cargo = ["EMPLEADO", "TECNICO", "PRACTICANTE", "SUPERVISOR"]
    opciones_area = ["FINANZAS", "REDES", "MANTENIMIENTO", "ALMACEN", "INTERNO"]

    tk.Label(frame_contenido, text="Cargo").pack()
    ttk.Combobox(frame_contenido, textvariable=var_cargo, values=opciones_cargo, state="readonly").pack(pady=5)

    tk.Label(frame_contenido, text="Área").pack()
    ttk.Combobox(frame_contenido, textvariable=var_area, values=opciones_area, state="readonly").pack(pady=5)

    label_foto = tk.Label(frame_contenido)
    label_foto.pack(pady=5)

    # ============== Tomar Foto =================
    def tomar_foto():
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            ruta = os.path.join(CARPETA_USUARIOS, f"{id_auto}.jpg")
            cv2.imwrite(ruta, frame)
            imagen = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(imagen.resize((200, 200)))
            label_foto.configure(image=img_tk)
            label_foto.image = img_tk
            foto_tomada[0] = ruta
            messagebox.showinfo("Foto tomada", "La foto ha sido capturada correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")

    tk.Button(frame_contenido, text="Tomar Foto", command=tomar_foto).pack(pady=5)

    # ============== Guardar datos y volver =================
    def guardar_datos():
        if not all([var_nombre.get(), var_apellido.get(), var_cargo.get(), var_area.get()]):
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return
        if not foto_tomada[0]:
            messagebox.showerror("Error", "Debe tomar una foto antes de registrar.")
            return

        existe_archivo = os.path.exists(USUARIOS_CSV)
        with open(USUARIOS_CSV, "a", newline='') as f:
            campos = ["ID", "Nombre", "Apellido", "Cargo", "Área"]
            writer = csv.DictWriter(f, fieldnames=campos)
            if not existe_archivo:
                writer.writeheader()
            writer.writerow({
                "ID": id_auto,
                "Nombre": var_nombre.get(),
                "Apellido": var_apellido.get(),
                "Cargo": var_cargo.get(),
                "Área": var_area.get()
            })

        # Ejecutar jpg_a_data.py
        subprocess.run(["python", "jpg_a_data.py"])

        messagebox.showinfo("Registro completado", "El usuario fue registrado correctamente.")
        ir_a_reconocimiento()

    # ============== Volver a reconocimiento ==============
    def ir_a_reconocimiento():
        from main import mostrar_reconocimiento
        mostrar_reconocimiento(root, frame_contenido, label_video, info_usuario, btn_reconocer)

    tk.Button(frame_contenido, text="Registrar Usuario", command=guardar_datos, bg="#4CAF50", fg="white").pack(pady=10)
    tk.Button(frame_contenido, text="Cancelar", command=ir_a_reconocimiento, bg="#f44336", fg="white").pack()
