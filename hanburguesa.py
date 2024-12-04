import tkinter as tk
from tkinter import ttk, messagebox  # Para mostrar mensajes de error
from PIL import Image, ImageTk  # Pillow para manejar imágenes avanzadas
import oracledb
oracledb.init_oracle_client() #inicializar la tabla

# Función para mostrar un mensaje de error
def mostrar_error(mensaje):
    messagebox.showerror("Error", mensaje)
    
#Obtener coneccion a la base
def obtener_conexion():
    try:
        conexion = oracledb.connect(
            user='SYSTEM',
            password='108310',
            dsn='localhost/xe'
        )
        return conexion
    except oracledb.DatabaseError as err:
        messagebox.showerror("Error", f"Error de conexión a la base de datos: {err}")
        return None

# Ventana de inicio de sesión
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión")
ventana_login.geometry("300x200")
ventana_login.resizable(False, False)

# Etiquetas y campos de entrada
tk.Label(ventana_login, text="Usuario:").pack(pady=5)
entrada_usuario = tk.Entry(ventana_login, width=30)
entrada_usuario.pack(pady=5)

tk.Label(ventana_login, text="Contraseña:").pack(pady=5)
entrada_contrasena = tk.Entry(ventana_login, show="*", width=30)
entrada_contrasena.pack(pady=5)

# Función para validar las credenciales
def validar_credenciales():
    usuario = entrada_usuario.get()
    contrasena = entrada_contrasena.get()
    if usuario == "admin" and contrasena == "1234":  # Credenciales predeterminadas
        abrir_ventana_principal(usuario, contrasena)
    elif usuario == "emplo" and contrasena == "4321": 
        abrir_ventana_principal(usuario, contrasena)
    else:
        mostrar_error("Usuario o contraseña incorrectos")

# Botón de inicio de sesión
tk.Button(ventana_login, text="Iniciar Sesión", command=validar_credenciales).pack(pady=20)



# Función para abrir la ventana principal después del inicio de sesión exitoso
def abrir_ventana_principal(us, cont):
    pos_x = ventana_login.winfo_x()
    pos_y = ventana_login.winfo_y()
    ventana_login.destroy()  # Cerrar la ventana de inicio de sesión

    # Crear la ventana principal
    ventana = tk.Tk()
    ventana.title("VENTAS E INSUMOS")
    ventana.geometry(f"400x400+{pos_x}+{pos_y}")
    ventana.resizable(False, False)

# Función para abrir la ventana de Ventas
    def ventana_ventas():
        pos_x = ventana.winfo_x()
        pos_y = ventana.winfo_y()
    
        nueva_ventana = tk.Tk()
        nueva_ventana.title("Ventas")
        nueva_ventana.geometry(f"400x500+{pos_x}+{pos_y}")
    
        tk.Label(nueva_ventana, text="ID DEL PRODUCTO").pack(pady=5)
        entrada_id_producto = tk.Entry(nueva_ventana, width=30)
        entrada_id_producto.pack(pady=5)
    
        tk.Label(nueva_ventana, text="CANTIDAD DE ALIMENTO").pack(pady=5)
        entrada_cantidad = tk.Entry(nueva_ventana, width=30)
        entrada_cantidad.pack(pady=5)
    
        tk.Label(nueva_ventana, text="DIRECCIÓN").pack(pady=5)
        entrada_direccion = tk.Entry(nueva_ventana, width=30)
        entrada_direccion.pack(pady=5)
    
        tk.Label(nueva_ventana, text="NOMBRE DEL CLIENTE").pack(pady=5)
        entrada_cliente = tk.Entry(nueva_ventana, width=30)
        entrada_cliente.pack(pady=5)
    
        def insertar_pedido():
            """
            Inserta los datos ingresados en la tabla 'PedidoDetalles' y luego en 'Pedidos'.
            """
            id_producto = entrada_id_producto.get()
            cantidad = entrada_cantidad.get()
            direccion = entrada_direccion.get()
            nombre_cliente = entrada_cliente.get()

            # Validar entradas
            if not id_producto or not cantidad or not direccion or not nombre_cliente:
                mostrar_error("Por favor, completa todos los campos.")
                return

            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser un número positivo.")
            except ValueError as e:
                mostrar_error(f"Error en el campo 'Cantidad': {e}")
                return

            # Conexión a la base de datos
            conexion = obtener_conexion()
            if conexion is None:
                return

            try:
                cursor = conexion.cursor()

                # Generar un nuevo ID para 'PedidoDetalles'
                cursor.execute("SELECT 'P'||LPAD(TO_CHAR(NVL(MAX(TO_NUMBER(SUBSTR(id_pedido, 2))), 0) + 1), 11, '0') FROM HR.PedidoDetalles")
                nuevo_id_pedido = cursor.fetchone()[0]

                # Insertar en la tabla 'PedidoDetalles'
                cursor.execute("""
                    INSERT INTO HR.PedidoDetalles (id_pedido, fecha_pedido, hora_pedido)
                    VALUES (:id_pedido, TO_DATE('2024-12-01', 'YYYY-MM-DD'), SYSTIMESTAMP)
                """, {"id_pedido": nuevo_id_pedido})

                # Obtener el precio del alimento desde la tabla Alimentos
                cursor.execute("SELECT precio FROM HR.Alimentos WHERE id_alimento = :id_producto", {"id_producto": id_producto})
                resultado = cursor.fetchone()

                if not resultado:
                    mostrar_error(f"No se encontró el producto con ID {id_producto}.")
                    return

                precio_alimento = resultado[0]
                total_pedido = precio_alimento * cantidad

                # Insertar en la tabla 'Pedidos' utilizando el mismo id_pedido
                cursor.execute("""
                    INSERT INTO HR.Pedidos (id_pedido, id_alimento, cantidad_alimento, total_pedido, direccion, nombre_cliente)
                    VALUES (:id_pedido, :id_alimento, :cantidad, :total, :direccion, :nombre_cliente)
                """, {
                    "id_pedido": nuevo_id_pedido,
                    "id_alimento": id_producto,
                    "cantidad": cantidad,
                    "total": total_pedido,
                    "direccion": direccion,
                    "nombre_cliente": nombre_cliente
                })

                # Confirmar transacción
                conexion.commit()

                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", f"Pedido guardado con ID {nuevo_id_pedido}.")

                # Limpiar campos
                entrada_id_producto.delete(0, tk.END)
                entrada_cantidad.delete(0, tk.END)
                entrada_direccion.delete(0, tk.END)
                entrada_cliente.delete(0, tk.END)

            except oracledb.DatabaseError as err:
                conexion.rollback()  # Revertir en caso de error
                mostrar_error(f"Error al guardar el pedido: {err}")
            finally:
                conexion.close()

        # Botón para registrar el pedido
        tk.Button(nueva_ventana, text="Registrar Pedido", command=insertar_pedido).pack(pady=20)
        tk.Button(nueva_ventana, text="VER PEDIDOS EN CURSO", command=abrir_ventas).pack(pady=20)
        tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=20)
        nueva_ventana.mainloop()


    # Función para abrir la ventana de Insumos
    def ventana_insumos():
        pos_x = ventana.winfo_x()
        pos_y = ventana.winfo_y()
        
        nueva_ventana = tk.Tk()
        nueva_ventana.title("INSUMOS")
        nueva_ventana.geometry(f"400x400+{pos_x}+{pos_y}")
        
        tk.Label(nueva_ventana, text="NOMBRE").pack(pady=5)
        tk.Entry(nueva_ventana, width=30).pack(pady=5)
        tk.Label(nueva_ventana, text="FECHA DE CADUCIDAD").pack(pady=5)
        tk.Entry(nueva_ventana, width=30).pack(pady=5)
        tk.Label(nueva_ventana, text="CANTIDAD").pack(pady=5)
        tk.Entry(nueva_ventana, width=30).pack(pady=5)
        
        tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=20)
        tk.Button(nueva_ventana, text="INVENTARIO", command=lambda: abrir_inventario(us, cont)).pack(pady=20)
        nueva_ventana.mainloop()

    # Cargar la imagen de fondo
    try:
        imagen_fondo = Image.open("fondo.png").resize((400, 400), Image.Resampling.LANCZOS)
        fondo = ImageTk.PhotoImage(imagen_fondo)
    except Exception as e:
        mostrar_error(f"No se pudo cargar el fondo: {e}")
        fondo = None

    # Cargar el logo
    try:
        imagen_logo = Image.open("logo.png").resize((200, 200), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen_logo)
    except Exception as e:
        mostrar_error(f"No se pudo cargar el logo: {e}")
        logo = None

    if fondo:
        fondo_label = tk.Label(ventana, image=fondo)
        fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

    if logo:
        logo_label = tk.Label(ventana, image=logo)
        logo_label.place(relx=0.5, rely=0.35, anchor="center")  # Centrado un poco más arriba

    # Botón de Ventas
    boton_ventas = tk.Button(ventana, text="VENTAS", font=("Arial", 14), bg="white", fg="black", command=ventana_ventas)
    boton_ventas.place(relx=0.5, rely=0.70, anchor="center")

     # Botón de Insumos
    if us == "admin" and cont == "1234": 
        boton_insumos = tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=ventana_insumos)
        boton_insumos.place(relx=0.5, rely=0.83, anchor="center")
    elif us == "emplo" and cont == "4321": 
        boton_insumos = tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=lambda: abrir_inventario(us, cont))
        boton_insumos.place(relx=0.5, rely=0.83, anchor="center")

    ventana.mainloop()

def abrir_inventario(us, cont):
    # Crear nueva ventana
    nueva_ventana = tk.Tk()
    nueva_ventana.title("Inventario Actual")
    nueva_ventana.state("zoomed")

    # Etiqueta de título
    tk.Label(nueva_ventana, text="Inventario Actual", font=("Arial", 18, "bold")).pack(pady=10)
    
    # Crear un marco para la tabla
    frame_tabla = tk.Frame(nueva_ventana)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

    # Mostrar datos
    tree = ttk.Treeview(frame_tabla, columns=("id_insumo", "nombre_insumo", "cantidad"), show="headings", height=20)
    tree.heading("id_insumo", text="Código del insumo")
    tree.heading("nombre_insumo", text="Nombre del Insumo")
    tree.heading("cantidad", text="Existencias Actuales")
    
    tree.column("id_insumo", width=300, anchor="center")
    tree.column("nombre_insumo", width=300, anchor="center")
    tree.column("cantidad", width=150, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    # Scrollbar para la tabla
    scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Configurar etiquetas de color
    tree.tag_configure('muchas_existencias', foreground="blue")
    tree.tag_configure('medias_existencias', foreground="orange")
    tree.tag_configure('pocas_existencias', foreground="red")

    def cargar_datos(filtro=""):
        """
        Carga los datos en el Treeview según el filtro proporcionado y aplica colores.
        """
        conexion = obtener_conexion()
        if conexion is None:
            return  
        
        try:
            cursor = conexion.cursor()
            query = '''
            SELECT i.id_insumo, i.nombre_insumo, COALESCE(v.cantidad, 0) AS cantidad
            FROM HR.Insumos i
            LEFT JOIN HR.VencInsumos v ON i.id_insumo = v.id_insumo
            WHERE LOWER(i.nombre_insumo) LIKE :filtro

            '''
            cursor.execute(query, {"filtro": f"%{filtro.lower()}%"})
            
            # Limpiar la tabla antes de insertar nuevos datos
            for item in tree.get_children():
                tree.delete(item)
            
            # Insertar datos en la tabla con colores según la cantidad
            resultados = cursor.fetchall()
            for fila in resultados:
                id_insumo, nombre_insumo, cantidad = fila
                if cantidad > 50:  # Muchas existencias
                    tag = 'muchas_existencias'
                elif cantidad >= 20 and cantidad <= 50:  # Medias existencias
                    tag = 'medias_existencias'
                elif cantidad < 20:  # Pocas existencias
                    tag = 'pocas_existencias'
                tree.insert("", "end", values=fila, tags=(tag,))
        except Exception as err:
            messagebox.showerror("Error", f"Error al ejecutar la consulta: {err}")
        finally:
            conexion.close()

    # Función para manejar el evento de búsqueda
    def buscar(event):
        filtro = entry_busqueda.get()
        cargar_datos(filtro)

    def eliminar_fila():
        try:
            # Obtener el ID de la fila seleccionada
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, selecciona una fila para eliminar.")
                return
            
            item = tree.item(seleccion)
            valores = item['values']
            id_insumo= valores[0]  # Obtener el ID del pedido
            
            conexion = obtener_conexion()
            if conexion is None:
                return  
            # Eliminar de la base de datos
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM HR.VencInsumos WHERE id_insumo = :1", (id_insumo,))
                cursor.execute("DELETE FROM HR.Insumos WHERE id_insumo = :1", (id_insumo,))
                conexion.commit()

            except oracledb.DatabaseError as err:
                messagebox.showerror("Error", f"Error al eliminar el registro: {err}")
                return
            finally:
                conexion.close()
            
            # Eliminar la fila del Treeview
            tree.delete(seleccion)
            messagebox.showinfo("Éxito", f"Registro con ID {id_insumo} eliminado correctamente.")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la fila: {e}")

    # Cargar los datos al abrir la ventana
    cargar_datos()

    if us == "admin" and cont == "1234":
        #Boton para borrar registro de inventarios
        boton_eliminar = tk.Button(nueva_ventana, text="Eliminar insumo", font=("Arial", 14), command=eliminar_fila)
        boton_eliminar.pack(pady=10)

    # Etiqueta y campo de búsqueda
    tk.Label(nueva_ventana, text="¿Qué desea buscar?").pack(pady=5)
    entry_busqueda = tk.Entry(nueva_ventana, width=30)
    entry_busqueda.pack(pady=5)
    entry_busqueda.bind("<KeyRelease>", buscar)  # Vincula el evento de teclado con la función buscar

    # Botón para cerrar la ventana
    boton_cerrar = tk.Button(nueva_ventana, text="Cerrar", font=("Arial", 14), command=nueva_ventana.destroy)
    boton_cerrar.pack(pady=10)
    
    nueva_ventana.mainloop()

#VENTANAS DE VENTAS
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
    
    # Función para cargar los datos desde la base de datos en ventanda de ventas
    def cargar_datos():
        conexion = obtener_conexion()
        if conexion is None:
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
    
    #funcion para eliminar elementos de ventas
    def eliminar_fila():
        try:
            # Obtener el ID de la fila seleccionada
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, selecciona una fila para eliminar.")
                return
            
            item = tree.item(seleccion)
            valores = item['values']
            id_pedido = valores[0]  # Obtener el ID del pedido
            
            conexion = obtener_conexion()
            if conexion is None:
                return  
            # Eliminar de la base de datos
            try:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM HR.PedidoDetalles WHERE id_pedido = :1", (id_pedido,))
                conexion.commit()

            except oracledb.DatabaseError as err:
                messagebox.showerror("Error", f"Error al eliminar el registro: {err}")
                return
            finally:
                conexion.close()
            
            # Eliminar la fila del Treeview
            tree.delete(seleccion)
            messagebox.showinfo("Éxito", f"Registro con ID {id_pedido} eliminado correctamente.")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la fila: {e}")
    # Cargar los datos al abrir la ventana
    cargar_datos()
    
    #Boton para borrar registro de ventas
    boton_eliminar = tk.Button(nueva_ventana, text="Eliminar Pedido", font=("Arial", 14), command=eliminar_fila)
    boton_eliminar.pack(pady=10)
    
    def cerrar_ventana():
        nueva_ventana.destroy()
    
    # Botón para cerrar la ventana
    boton_cerrar = tk.Button(nueva_ventana, text="Cerrar", font=("Arial", 14), command=cerrar_ventana)
    boton_cerrar.pack(pady=10)
    
    nueva_ventana.mainloop()

ventana_login.mainloop()