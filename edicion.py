import sqlite3

conn = sqlite3.connect("mi_base.db")
cursor = conn.cursor()

# Actualizar apellidos
cursor.execute("UPDATE usuarios SET Apellido = 'CHAVEZ' WHERE ID = 'USER002';")
cursor.execute("UPDATE usuarios SET Apellido = 'MISAICO' WHERE ID = 'USER003';")

conn.commit()
conn.close()

print("Actualizaciones realizadas correctamente.")
