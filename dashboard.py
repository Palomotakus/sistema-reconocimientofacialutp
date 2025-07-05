import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import sys
import os

def volver_a_main(self):
    self.root.destroy()
    python = sys.executable
    os.execl(python, python, "main.py")


DB_PATH = "mi_base.db"

class DashboardInventario:
    def __init__(self, root, on_cerrar=None, on_detener=None):
        self.root = root
        self.on_cerrar = on_cerrar
        self.on_detener = on_detener
        self.root.title("Dashboard de Inventario - Sistemas de Aire Acondicionado")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f2f5")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.crear_tabla_si_no_existe()

        self.main_frame = tk.Frame(root, bg="#f0f2f5")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        top_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        top_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(top_frame, text="INVENTARIO DE SISTEMAS DE AIRE ACONDICIONADO", 
                font=("Helvetica", 16, "bold"), bg="#f0f2f5").pack(side=tk.LEFT)

        btn_salir = tk.Button(top_frame, text="Volver al menú", command=self.volver_a_main,
                      font=("Helvetica", 10), bg="#e74a3b", fg="white", padx=10)
        btn_salir.pack(side=tk.RIGHT)

        self.search_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        self.search_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(self.search_frame, text="Buscar:", font=("Helvetica", 10), bg="#f0f2f5").pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var, width=40, font=("Helvetica", 10))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.buscar_producto)

        self.search_button = tk.Button(self.search_frame, text="Buscar", command=self.buscar_producto, 
                                     bg="#4e73df", fg="white", font=("Helvetica", 10))
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))

        self.add_button = tk.Button(self.search_frame, text="+ Agregar Producto", command=self.agregar_producto,
                                  bg="#1cc88a", fg="white", font=("Helvetica", 10))
        self.add_button.pack(side=tk.RIGHT)

        self.tree_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Nombre", "Descripción", "Precio", "Stock", "Visibilidad"), 
                                show="headings", selectmode="browse")

        columnas = [("ID", 50), ("Nombre", 150), ("Descripción", 300), ("Precio", 100), ("Stock", 80), ("Visibilidad", 80)]
        for col, width in columnas:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=width, minwidth=width)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.action_frame = tk.Frame(self.main_frame, bg="#f0f2f5")
        self.action_frame.pack(fill=tk.X, pady=(15, 0))

        self.toggle_visibility_button = tk.Button(self.action_frame, text="Cambiar Visibilidad", 
                                                command=self.cambiar_visibilidad, bg="#f6c23e", fg="white")
        self.toggle_visibility_button.pack(side=tk.LEFT, padx=(0, 10))

        self.edit_button = tk.Button(self.action_frame, text="Editar Producto", command=self.editar_producto,
                                   bg="#36b9cc", fg="white")
        self.edit_button.pack(side=tk.LEFT, padx=(0, 10))

        self.delete_button = tk.Button(self.action_frame, text="Eliminar Producto", command=self.eliminar_producto,
                                     bg="#e74a3b", fg="white")
        self.delete_button.pack(side=tk.LEFT)

        self.cargar_datos()

    def volver_a_main(self):
        if self.on_detener:
            try:
              self.on_detener()
            except Exception as e:
              print(f"Error al detener la cámara: {e}")

        self.root.destroy()



    def crear_tabla_si_no_existe(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                visibilidad TEXT CHECK(visibilidad IN ('SI', 'NO')) NOT NULL DEFAULT 'SI'
            )
        """)
        self.conn.commit()

    def cargar_datos(self, filtro=None):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT * FROM inventario"
        params = ()

        if filtro:
            query += " WHERE id LIKE ? OR nombre LIKE ? OR descripcion LIKE ?"
            filtro_param = f"%{filtro}%"
            params = (filtro_param, filtro_param, filtro_param)

        for row in self.cursor.execute(query, params):
            tag = 'visible' if row[5] == 'SI' else 'oculto'
            self.tree.insert("", tk.END, values=(row[0], row[1], row[2], f"${row[3]:,.2f}", row[4], row[5]), tags=(tag,))

        self.tree.tag_configure('visible', background='#e8f4f8')
        self.tree.tag_configure('oculto', background='#f8d7da')

    def buscar_producto(self, event=None):
        filtro = self.search_var.get()
        self.cargar_datos(filtro)

    def agregar_producto(self):
        from tkinter.simpledialog import askstring

        def guardar():
            try:
                self.cursor.execute("""
                    INSERT INTO inventario (nombre, descripcion, precio, stock, visibilidad)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre.get(), descripcion.get(), float(precio.get()), int(stock.get()), visibilidad.get()))
                self.conn.commit()
                add_win.destroy()
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Producto agregado correctamente")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        add_win = tk.Toplevel(self.root)
        add_win.title("Agregar Producto")
        add_win.geometry("400x300")
        add_win.grab_set()

        nombre, descripcion, precio, stock, visibilidad = [tk.StringVar() for _ in range(5)]
        visibilidad.set("SI")

        for i, (label, var) in enumerate([
            ("Nombre", nombre),
            ("Descripción", descripcion),
            ("Precio", precio),
            ("Stock", stock)
        ]):
            tk.Label(add_win, text=label).pack()
            tk.Entry(add_win, textvariable=var).pack()

        ttk.Combobox(add_win, values=["SI", "NO"], textvariable=visibilidad, state="readonly").pack(pady=10)

        tk.Button(add_win, text="Guardar", command=guardar, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(add_win, text="Cancelar", command=add_win.destroy).pack()

    def cambiar_visibilidad(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        id_producto = self.tree.item(item[0])['values'][0]
        visibilidad_actual = self.tree.item(item[0])['values'][5]
        nueva = 'NO' if visibilidad_actual == 'SI' else 'SI'
        self.cursor.execute("UPDATE inventario SET visibilidad = ? WHERE id = ?", (nueva, id_producto))
        self.conn.commit()
        self.cargar_datos()

    def editar_producto(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        id_producto = self.tree.item(item[0])['values'][0]

        self.cursor.execute("SELECT nombre, descripcion, precio, stock, visibilidad FROM inventario WHERE id = ?", (id_producto,))
        producto = self.cursor.fetchone()
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return

        def guardar():
            try:
                self.cursor.execute("""
                    UPDATE inventario
                    SET nombre = ?, descripcion = ?, precio = ?, stock = ?, visibilidad = ?
                    WHERE id = ?
                """, (nombre.get(), descripcion.get(), float(precio.get()), int(stock.get()), visibilidad.get(), id_producto))
                self.conn.commit()
                edit_win.destroy()
                self.cargar_datos()
                messagebox.showinfo("Éxito", "Producto actualizado")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Editar Producto")
        edit_win.geometry("400x300")
        edit_win.grab_set()

        nombre, descripcion, precio, stock, visibilidad = [tk.StringVar(value=str(producto[i])) for i in range(5)]

        for i, (label, var) in enumerate([
            ("Nombre", nombre),
            ("Descripción", descripcion),
            ("Precio", precio),
            ("Stock", stock)
        ]):
            tk.Label(edit_win, text=label).pack()
            tk.Entry(edit_win, textvariable=var).pack()

        ttk.Combobox(edit_win, values=["SI", "NO"], textvariable=visibilidad, state="readonly").pack(pady=10)

        tk.Button(edit_win, text="Guardar", command=guardar, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(edit_win, text="Cancelar", command=edit_win.destroy).pack()

    def eliminar_producto(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return

        id_producto = self.tree.item(item[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            self.cursor.execute("DELETE FROM inventario WHERE id = ?", (id_producto,))
            self.conn.commit()
            self.cargar_datos()
            messagebox.showinfo("Éxito", "Producto eliminado")

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardInventario(root)
    root.mainloop()
