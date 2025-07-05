import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import os
import subprocess
import sqlite3

DB_PATH = "mi_base.db"
CARPETA_USUARIOS = "usuarios"

def cargar_usuarios_desde_db():
    conn = sqlite3.connect("mi_base.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellido, cargo, area, acceso_dashboard FROM usuarios")
    resultados = cursor.fetchall()
    conn.close()

    usuarios = {}
    for fila in resultados:
        usuarios[fila[0]] = {
            "nombre": fila[1],
            "apellido": fila[2],
            "cargo": fila[3],
            "area": fila[4],
            "acceso_dashboard": fila[5]
        }
    return usuarios


def generar_nuevo_id():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE id LIKE 'USER%'")
        ids = cursor.fetchall()
        conn.close()

        nums = []
        for (id_str,) in ids:
            try:
                num = int(id_str[4:])
                nums.append(num)
            except ValueError:
                continue

        nuevo_num = max(nums) + 1 if nums else 1
        return f"USER{nuevo_num:03d}"

    except Exception as e:
        messagebox.showerror("Error", f"Error al generar ID: {str(e)}")
        return "USER001"

def crear_apartado_registro(frame_registro, frame_principal, cap, datos_usuarios, btn_reconocer):
    for widget in frame_registro.winfo_children():
        widget.destroy()

    id_auto = generar_nuevo_id()
    var_nombre = tk.StringVar()
    var_apellido = tk.StringVar()
    var_cargo = tk.StringVar()
    var_area = tk.StringVar()
    foto_tomada = [None]

    # Título
    tk.Label(frame_registro, text="Registro de Nuevo Usuario", 
            font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=(10, 5))
    
    tk.Label(frame_registro, text=f"ID asignado: {id_auto}", 
            font=("Arial", 12), bg="#f0f0f0").pack()

    # Formulario
    form_frame = tk.Frame(frame_registro, bg="#f0f0f0")
    form_frame.pack(pady=10)

    left_frame = tk.Frame(form_frame, bg="#f0f0f0")
    left_frame.grid(row=0, column=0, padx=10)

    tk.Label(left_frame, text="Nombre:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", pady=2)
    tk.Entry(left_frame, textvariable=var_nombre, width=25).grid(row=0, column=1, pady=2)

    tk.Label(left_frame, text="Apellido:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", pady=2)
    tk.Entry(left_frame, textvariable=var_apellido, width=25).grid(row=1, column=1, pady=2)

    right_frame = tk.Frame(form_frame, bg="#f0f0f0")
    right_frame.grid(row=0, column=1, padx=10)

    opciones_cargo = ["EMPLEADO", "TÉCNICO", "PRACTICANTE", "SUPERVISOR"]
    opciones_area = ["FINANZAS", "REDES", "MANTENIMIENTO", "ALMACÉN", "INTERNA"]

    tk.Label(right_frame, text="Cargo:", bg="#f0f0f0").grid(row=0, column=0, sticky="e", pady=2)
    ttk.Combobox(right_frame, textvariable=var_cargo, values=opciones_cargo, 
                state="readonly", width=22).grid(row=0, column=1, pady=2)

    tk.Label(right_frame, text="Área:", bg="#f0f0f0").grid(row=1, column=0, sticky="e", pady=2)
    ttk.Combobox(right_frame, textvariable=var_area, values=opciones_area, 
                state="readonly", width=22).grid(row=1, column=1, pady=2)

    def tomar_foto():
        if cap is None:
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            return
            
        ret, frame = cap.read()
        if ret:
            if not os.path.exists(CARPETA_USUARIOS):
                os.makedirs(CARPETA_USUARIOS)
                
            ruta = os.path.join(CARPETA_USUARIOS, f"{id_auto}.jpg")
            cv2.imwrite(ruta, frame)

            imagen = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imagen = imagen.resize((150, 150))
            img_tk = ImageTk.PhotoImage(image=imagen)
            
            if not hasattr(frame_registro, 'preview_foto'):
                frame_registro.preview_foto = tk.Label(frame_registro)
                frame_registro.preview_foto.pack(pady=5)
                
            frame_registro.preview_foto.config(image=img_tk)
            frame_registro.preview_foto.image = img_tk
            
            foto_tomada[0] = ruta
            messagebox.showinfo("Foto tomada", "La foto ha sido capturada correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo capturar la foto.")

    tk.Button(frame_registro, text="Tomar Foto", command=tomar_foto).pack(pady=10)

    btn_frame = tk.Frame(frame_registro, bg="#f0f0f0")
    btn_frame.pack(pady=10)

    def guardar_datos():
        if not all([var_nombre.get(), var_apellido.get(), var_cargo.get(), var_area.get()]):
            messagebox.showerror("Error", "Por favor complete todos los campos.")
            return
        if not foto_tomada[0]:
            messagebox.showerror("Error", "Debe tomar una foto antes de registrar.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (id, nombre, apellido, cargo, area, acceso_dashboard)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_auto, var_nombre.get(), var_apellido.get(), var_cargo.get(), var_area.get(), "SI"))
            conn.commit()
            conn.close()

            datos_usuarios.clear()
            datos_usuarios.update(cargar_usuarios_desde_db())

            subprocess.run(["python", "jpg_a_data.py"], check=True)
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            volver_a_principal()
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar en base de datos: {str(e)}")

    def volver_a_principal():
        frame_principal.tkraise()
        btn_reconocer.config(state="normal")

    tk.Button(btn_frame, text="Registrar", bg="#4CAF50", fg="white", width=12,
             command=guardar_datos).pack(side=tk.LEFT, padx=10)
    
    tk.Button(btn_frame, text="Cancelar", bg="#f44336", fg="white", width=12,
             command=volver_a_principal).pack(side=tk.LEFT, padx=10)
