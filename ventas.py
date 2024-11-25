import tkinter as tk
from tkinter import ttk, messagebox
import oracledb

oracledb.init_oracle_client() #inicializar la tabla

def abrir_ventas():
    # Crear nueva ventana
    nueva_ventana = tk.Tk()
    nueva_ventana.title("Ventas")
    nueva_ventana.state("zoomed")
    
    # Etiqueta de título
    tk.Label(nueva_ventana, text="Detalles de los pedidos", font=("Arial", 18, "bold")).pack(pady=10)
    
    # Crear un marco para la tabla
    frame_tabla = tk.Frame(nueva_ventana)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Mostrar datos
    tree = ttk.Treeview(frame_tabla, columns=("id_pedido", "fecha_pedido", "hora_pedido"), show="headings", height=20)
    tree.heading("id_pedido", text="ID Pedido")
    tree.heading("fecha_pedido", text="Fecha Pedido")
    tree.heading("hora_pedido", text="Hora Pedido")
    
    tree.column("id_pedido", width=150, anchor="center")
    tree.column("fecha_pedido", width=150, anchor="center")
    tree.column("hora_pedido", width=200, anchor="center")
    
    tree.pack(side="left", fill="both", expand=True)
    
    # Scrollbar para la tabla
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Función para cargar los datos desde la base de datos
    def cargar_datos():
        try:
            # Conectar a la base de datos
            conexion = oracledb.connect(
                user='SYSTEM',
                password='108310',
                dsn='localhost/xe'
            )
        except oracledb.DatabaseError as err:
            messagebox.showerror("Error", f"Error de conexión a la base de datos: {err}")
            return
        
        try:
            cursor = conexion.cursor()
            query = '''SELECT id_pedido, TO_CHAR(fecha_pedido, 'YYYY-MM-DD'), TO_CHAR(hora_pedido, 'HH24:MI:SS') FROM HR.PedidoDetalles'''
            cursor.execute(query)
            
            # Insertar datos en la tabla
            resultados = cursor.fetchall()
            for fila in resultados:
                tree.insert("", "end", values=fila)
        except Exception as err:
            messagebox.showerror("Error", f"Error al ejecutar la consulta: {err}")
        finally:
            conexion.close()
    
    # Cargar los datos al abrir la ventana
    cargar_datos()
    
    # Botón para cerrar la ventana
    def cerrar_ventana():
        nueva_ventana.destroy()
    
    boton_cerrar = tk.Button(nueva_ventana, text="Cerrar", font=("Arial", 14), command=cerrar_ventana)
    boton_cerrar.pack(pady=10)
    
    nueva_ventana.mainloop()
