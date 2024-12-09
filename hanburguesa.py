import tkinter as tk
import datetime
from tkinter import ttk, messagebox  # Para mostrar mensajes de error
from PIL import Image, ImageTk  # Pillow para manejar imágenes avanzadas
from ttkthemes import ThemedTk
import oracledb
#oracledb.init_oracle_client(r'C:\Users\pablo\Oracle Client\instantclient_19_25') #inicializar
oracledb.init_oracle_client() #inicializar
#================= ESTA ES LA UNICA COSA QUE VAN A CAMBIAR PARA LA DATABASE ============#
passwd='108310'
schema='HR'
#=======================================================================================#
class hanburguesa:
    def __init__(self):
        self.inicio_de_sesion()
        self.us = None
        self.rol = None
    def setus(self, us):
        self.us =  us
    def setrol(self, rol):
        self.rol = rol
    def getus(self):
        return self.us
    def getrol(self):
        return self.rol
    def mostrar_error(self, mensaje):
        messagebox.showerror("Error", mensaje)
    #Obtener coneccion a la base
    def obtener_conexion(self):
        try:
            conexion = oracledb.connect(
                user='SYSTEM',
                password=passwd,
                dsn='localhost/xe'
            )
            return conexion
        except oracledb.DatabaseError as err:
            messagebox.showerror("Error", f"Error de conexión a la base de datos: {err}")
            return None
    #Definir secuencias y tablas (las que sean necesarias)
    def instalardb(self):
        conexion=self.obtener_conexion()
        if conexion is None:
            return
        else:
            cursor=conexion.cursor()
            queryT1=f'''CREATE TABLE {schema}.UsuariosNom (
            id_usuario VARCHAR2(32) CONSTRAINT cv_usuario PRIMARY KEY, 
            nombre_usuario VARCHAR(32) NOT NULL, 
            contrasenia VARCHAR2(32) NOT NULL)
            '''
            queryT2=f'''CREATE TABLE {schema}.UsuariosRol (
            id_usuario VARCHAR2(32) CONSTRAINT cv_usuario_i REFERENCES {schema}.UsuariosNom(id_usuario), 
            rol CHAR(5) NOT NULL)
            '''
            queryT3=f'''CREATE TABLE {schema}.Insumos (
            id_insumo VARCHAR2(12) CONSTRAINT cv_insumo PRIMARY KEY,
            nombre_insumo VARCHAR(10) UNIQUE,
            unidad_medida CHAR(2) NOT NULL)
            '''
            queryT4=f'''CREATE TABLE {schema}.VencInsumos (
            id_insumo VARCHAR2(12) NOT NULL,
            caducidad DATE NOT NULL,
            cantidad NUMBER(8) NOT NULL,
            PRIMARY KEY (id_insumo, caducidad), 
            CONSTRAINT cvi_insumo_i FOREIGN KEY(id_insumo) REFERENCES {schema}.Insumos(id_insumo))
            '''
            queryT5=f'''CREATE TABLE {schema}.Alimentos (
            id_alimento VARCHAR2(12) CONSTRAINT cv_alimento PRIMARY KEY, 
            nombre_alimento VARCHAR(10) NOT NULL, 
            precio NUMBER(8,2) NOT NULL)
            '''
            queryT6=f'''CREATE TABLE {schema}.Pedidos (
            id_pedido VARCHAR(12) CONSTRAINT cv_pedido_i REFERENCES {schema}.PedidoDetalles(id_pedido),
            id_alimento VARCHAR2(12) CONSTRAINT cv_alimento_i REFERENCES {schema}.Alimentos(id_alimento), 
            cantidad_alimento NUMBER(5) NOT NULL, 
            total_pedido NUMBER(8,2) NOT NULL,
            direccion VARCHAR(72) NOT NULL,
            nombre_cliente VARCHAR(24) NOT NULL)
            '''
            queryT7=f'''CREATE TABLE {schema}.PedidoDetalles (
            id_pedido VARCHAR(12) CONSTRAINT cv_pedido PRIMARY KEY,
            fecha_pedido DATE NOT DEFAULT SYSDATE NULL,
            hora_pedido TIMESTAMP  WITH LOCAL TIME ZONE DEFAULT SYSTIMESTAMP NOT NULL)
            '''
            queryS1=f'''
            CREATE SEQUENCE {schema}.INSUM_SEQ
            INCREMENT BY 1
            START WITH 1
            MINVALUE 1
            '''
            queryS2=f'''
            CREATE SEQUENCE {schema}.USER_SEQ
            INCREMENT BY 1
            START WITH 1
            MINVALUE 1
            '''
            setadmin1=f'''INSERT INTO {schema}.UsuariosNom(id_usuario, nombre_usuario, contrasenia) VALUES ('0','ADMIN','hambre2024')'''
            setadmin2=f'''INSERT INTO {schema}.UsuariosRol(id_usuario, rol) VALUES ('0','Admin')'''
            querys=[queryT1,queryT2,queryT3,queryT4,queryT5,queryT7,queryT6,queryS1,queryS2]
            #Generar esquema
            for query in querys:
                try:
                    cursor.execute(query)
                except oracledb.DatabaseError as e:
                    pass
            #Setup admin
            try:
                #Comprueba que la ID existe
                cursor.execute(f'''SELECT id_usuario FROM {schema}.UsuariosRol WHERE id_usuario='0' ''')
                exists=cursor.fetchone
                if exists: #Solo si no existe
                    cursor.execute(setadmin1)
                    cursor.execute(setadmin2)
            except oracledb.DatabaseError as e:
                pass
            conexion.commit()
            cursor.close()
            conexion.close()
    def inicio_de_sesion(self):
        #Inicializar la base de datos
        self.instalardb()
        # Ventana de inicio de sesión
        ventana_login = ThemedTk(theme="black")
        ventana_login.title("Inicio de Sesión")
        ventana_login.geometry("300x320")
        ventana_login.resizable(False, False)
        
        try:
            imagen_logo = Image.open("user.png").resize((100, 100), Image.Resampling.LANCZOS)  # Ajusta el tamaño según sea necesario
            logo = ImageTk.PhotoImage(imagen_logo)
            logo_label = tk.Label(ventana_login, image=logo, bg="#f0f0f0")  # Cambié Label a tk.Label
            logo_label.pack(pady=10)  # Centra la imagen en la parte superior
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
        
        #Etiquetas y campos de entrada
        tk.Label(ventana_login, text="Usuario:").pack(pady=5)
        entrada_usuario = tk.Entry(ventana_login, width=30)
        entrada_usuario.pack(pady=5)
        tk.Label(ventana_login, text="Contraseña:").pack(pady=5)
        entrada_contrasena = tk.Entry(ventana_login, show="*", width=30)
        entrada_contrasena.pack(pady=5)
        # Botón de inicio de sesión
        # Función para validar las credenciales
        def validar_credenciales():
            usuario = entrada_usuario.get()
            contrasena = entrada_contrasena.get()
            def cargar_datos():
                conexion = self.obtener_conexion()
                if conexion is None:
                    return  
                try:
                    cursor = conexion.cursor()

                    # Consulta para validar credenciales y obtener el rol del usuario
                    query = f'''
                    SELECT UN.id_usuario, UR.rol
                    FROM {schema}.UsuariosNom UN
                    JOIN {schema}.UsuariosRol UR ON UN.id_usuario = UR.id_usuario
                    WHERE UN.nombre_usuario =:usuario AND UN.contrasenia =:contrasena
                    '''
                    cursor.execute(query, {"usuario": usuario, "contrasena": contrasena})
                    resultado = cursor.fetchone()
                    if resultado:
                        nombre, rol = resultado
                        self.setus(nombre)
                        self.setrol(rol)
                        # Llamar a la función que abre la ventana principal y pasar el rol
                        self.abrir_ventana_principal(ventana_login)
                    else:
                        # Mostrar mensaje de error si las credenciales no coinciden
                        self.mostrar_error("Usuario o contraseña incorrectos")
                except Exception as err:
                    messagebox.showerror("Error", f"Error al ejecutar la consulta: {err}")
                finally:
                    conexion.close()
            # Llamamos a cargar_datos para realizar la validación
            cargar_datos()
        tk.Button(ventana_login, text="Iniciar Sesión", command=validar_credenciales).pack(pady=20)
        ventana_login.mainloop()
    # Función para abrir la ventana principal después del inicio de sesión exitoso
    def abrir_ventana_principal(self, ventana_login):
        pos_x = ventana_login.winfo_x()
        pos_y = ventana_login.winfo_y()
        ventana_login.destroy()  # Cerrar la ventana de inicio de sesión

        # Crear la ventana principal
        ventana = tk.Tk()
        ventana.title("VENTAS E INSUMOS")
        ventana.geometry(f"400x500+{pos_x}+{pos_y}")
        ventana.resizable(False, False)

        def cerrar_sesion(caso):
            match caso:
                case 1:
                    ventana.destroy()
                    self.inicio_de_sesion()
                case 2:
                    self.abrir_inventario()
                case 3:
                    self.abrir_ventas()
                case 4:
                    self.abrir_usuarios()
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
                    self.mostrar_error("Por favor, completa todos los campos.")
                    return   
                try:
                    cantidad = int(cantidad)
                    if cantidad <= 0:
                        raise ValueError("La cantidad debe ser un número positivo.")
                except ValueError as e:
                    self.mostrar_error(f"Error en el campo 'Cantidad': {e}")
                    return
                # Conexión a la base de datos
                conexion = self.obtener_conexion()
                if conexion is None:
                    return
                try:
                    cursor = conexion.cursor()
                    # Generar un nuevo ID para 'PedidoDetalles'
                    cursor.execute(f"SELECT 'P'||LPAD(TO_CHAR(NVL(MAX(TO_NUMBER(SUBSTR(id_pedido, 2))), 0) + 1), 11, '0') FROM {schema}.PedidoDetalles")
                    nuevo_id_pedido = cursor.fetchone()[0]
                    # Insertar en la tabla 'PedidoDetalles'
                    cursor.execute(f"""
                        INSERT INTO {schema}.PedidoDetalles (id_pedido, fecha_pedido, hora_pedido)
                        VALUES (:id_pedido, TO_DATE('2024-12-01', 'YYYY-MM-DD'), SYSTIMESTAMP)
                    """, {"id_pedido": nuevo_id_pedido})
                     # Obtener el precio del alimento desde la tabla Alimentos
                    cursor.execute(f"SELECT precio FROM {schema}.Alimentos WHERE id_alimento = :id_producto", {"id_producto": id_producto})
                    resultado = cursor.fetchone()
                    if not resultado:
                        self.mostrar_error(f"No se encontró el producto con ID {id_producto}.")
                        return
                    precio_alimento = resultado[0]
                    total_pedido = precio_alimento * cantidad
                    # Insertar en la tabla 'Pedidos' utilizando el mismo id_pedido
                    cursor.execute(f"""
                        INSERT INTO {schema}.Pedidos (id_pedido, id_alimento, cantidad_alimento, total_pedido, direccion, nombre_cliente)
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
                    self.mostrar_error(f"Error al guardar el pedido: {err}")
                finally:
                    conexion.close()
            # Botón para registrar el pedido
            tk.Button(nueva_ventana, text="Registrar Pedido", command=insertar_pedido).pack(pady=20)
            tk.Button(nueva_ventana, text="VER PEDIDOS EN CURSO", command=lambda:cerrar_sesion(3)).pack(pady=20)
            tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=20)
            nueva_ventana.mainloop()
        # Función para abrir la ventana de Insumos
        def ventana_insumos():
            pos_x = ventana.winfo_x()
            pos_y = ventana.winfo_y()
            
            nueva_ventana = tk.Tk()
            nueva_ventana.title("INSUMOS")
            nueva_ventana.geometry(f"400x500+{pos_x}+{pos_y}")
            
            tk.Label(nueva_ventana, text="NOMBRE").pack(pady=5)
            entrada_nom_insumo=tk.Entry(nueva_ventana, width=30)
            entrada_nom_insumo.pack(pady=5)
            tk.Label(nueva_ventana, text="FECHA DE CADUCIDAD").pack(pady=5)
            entrada_fecha_cad=tk.Entry(nueva_ventana, width=30)
            entrada_fecha_cad.pack(pady=5)
            tk.Label(nueva_ventana, text="CANTIDAD").pack(pady=5)
            entrada_cant=tk.Entry(nueva_ventana, width=30)
            entrada_cant.pack(pady=5)
            tk.Label(nueva_ventana, text="UNIDAD DE MEDIDA").pack(pady=5)
            entrada_u_medida=tk.Entry(nueva_ventana, width=30)
            entrada_u_medida.pack(pady=5)
            def ingresar_insumo():
                nombre_insumo=entrada_nom_insumo.get()
                caducidad=entrada_fecha_cad.get()
                cantidad=entrada_cant.get()
                unidad_medida=entrada_u_medida.get()
                conexion=self.obtener_conexion()
                try:
                    cursor = conexion.cursor()
                    #Querys
                    checkquery=f'''SELECT id_insumo FROM {schema}.Insumos WHERE nombre_insumo=:nombre_insumo'''
                    query0=f'''INSERT INTO {schema}.VencInsumos(id_insumo, caducidad, cantidad) VALUES (:id_insumo, TO_DATE(:caducidad, 'DD-MM-YYYY'), :cantidad)'''
                    query1=f'''INSERT INTO {schema}.Insumos(id_insumo, nombre_insumo, unidad_medida) VALUES ({schema}.INSUM_SEQ.NEXTVAL, :nombre_insumo, :unidad_medida)'''
                    query2=f'''INSERT INTO {schema}.VencInsumos(id_insumo, caducidad, cantidad) VALUES ({schema}.INSUM_SEQ.CURRVAL, TO_DATE(:caducidad, 'DD-MM-YYYY'), :cantidad)'''
                    #Inputs
                    chkinput=(nombre_insumo,)
                    input1=(nombre_insumo, unidad_medida)
                    input2=(caducidad, cantidad)
                    #Ejecutar funcionalidad
                    cursor.execute(checkquery,chkinput)
                    exists=cursor.fetchone()
                    if exists is not None:
                        id_insumo=exists[0]
                        input0=(id_insumo,caducidad,cantidad)
                        cursor.execute(query0,input0)
                        messagebox.showinfo("Éxito",f"Insumo guardado con ID: {id_insumo}")
                    elif exists is None:
                        cursor.execute(query1,input1)
                        cursor.execute(query2,input2)
                        #Rastrear ID generado
                        cursor.execute(f"SELECT {schema}.INSUM_SEQ.CURRVAL FROM DUAL")
                        currID=cursor.fetchone()[0]
                        messagebox.showinfo("Éxito",f"Nuevo insumo guardado con la ID: {currID}")
                    conexion.commit()
                except Exception as err:
                    messagebox.showerror("Error", f"Error al ejecutar la consulta: {err}")
                finally:
                    conexion.close()
                #Aqui pongo mi avance de insumos
            tk.Button(nueva_ventana, text="INVENTARIO", command=lambda:cerrar_sesion(2)).pack(pady=15)
            tk.Button(nueva_ventana, text="AGREGAR",command=ingresar_insumo).pack(pady=15)
            tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=15)
            nueva_ventana.mainloop()

        def generar_id_unico():
            # Obtiene la fecha y hora actuales
            ahora = datetime.datetime.now()
            # Formatea la fecha y hora en un número único
            id_unico = ahora.strftime("%Y%m%d%H%M%S")  # Ejemplo: 20241208153045
            return id_unico

        def ventana_usuarios():
            pos_x = ventana.winfo_x()
            pos_y = ventana.winfo_y()
            
            nueva_ventana = tk.Tk()
            nueva_ventana.title("Usuarios")
            nueva_ventana.geometry(f"400x500+{pos_x}+{pos_y}")
            
            # Campos de entrada
            tk.Label(nueva_ventana, text="Nombre de Usuario").pack(pady=5)
            entrada_nom_usuario = tk.Entry(nueva_ventana, width=30)
            entrada_nom_usuario.pack(pady=5)
            
            tk.Label(nueva_ventana, text="Rol").pack(pady=5)
            selection_box = ttk.Combobox(nueva_ventana, values=["Admin", "User"], state="readonly", width=20)
            selection_box.pack(pady=5)
            selection_box.current(0)
            
            def ingresar_usuario():
                nombre_usuario = entrada_nom_usuario.get()
                id_usuario = generar_id_unico()  # Generar ID único basado en fecha/hora (8 caracteres)
                contrasenia = generar_id_unico()[8:]  # Contraseña generada automáticamente
                rol = selection_box.get()

                conexion = self.obtener_conexion()
                try:
                    cursor = conexion.cursor()
                    
                    # Inserción en la tabla UsuariosNom
                    query1 = f'''INSERT INTO {schema}.UsuariosNom (id_usuario, nombre_usuario, contrasenia)
                                VALUES (:id_usuario, :nombre_usuario, :contrasenia)'''
                    input1 = (id_usuario, nombre_usuario, contrasenia)
                    cursor.execute(query1, input1)
                    
                    # Inserción en la tabla UsuariosRol
                    query2 = f'''INSERT INTO {schema}.UsuariosRol (id_usuario, rol)
                                VALUES (:id_usuario, :rol)'''
                    input2 = (id_usuario, rol)
                    cursor.execute(query2, input2)
                    
                    conexion.commit()
                    messagebox.showinfo("Éxito", f"Usuario {nombre_usuario} con ID {id_usuario} y rol {rol} agregado correctamente.")
                except Exception as err:
                    messagebox.showerror("Error", f"Error al agregar usuario: {err}")
                finally:
                    conexion.close()

            # Botones
            tk.Button(nueva_ventana, text="Agregar Usuario", command=ingresar_usuario).pack(pady=15)
            tk.Button(nueva_ventana, text="Ver usuarios", command=lambda:cerrar_sesion(4)).pack(pady=15)
            tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=15)

            nueva_ventana.mainloop()

                #Aqui pongo mi avance de insumos
            tk.Button(nueva_ventana, text="USUARIOS", command=lambda:cerrar_sesion(4)).pack(pady=15)
            tk.Button(nueva_ventana, text="AGREGAR",command=ingresar_usuario).pack(pady=15)
            tk.Button(nueva_ventana, text="Cerrar", command=nueva_ventana.destroy).pack(pady=15)
            nueva_ventana.mainloop()

        '''
        # Cargar la imagen de fondo
        try:
            imagen_fondo = Image.open("fondo.png").resize((400, 400), Image.Resampling.LANCZOS)
            fondo = ImageTk.PhotoImage(imagen_fondo)
        except Exception as e:
            self.mostrar_error(f"No se pudo cargar el fondo: {e}")
            fondo = None
        if fondo:
            fondo_label = tk.Label(ventana, image=fondo)
            fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
        '''
        # Cargar el logo
        try:
            imagen_logo = Image.open("logo.png").resize((200, 200), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(imagen_logo)
        except Exception as e:
            self.mostrar_error(f"No se pudo cargar el logo: {e}")
            logo = None
        if logo:
            logo_label = tk.Label(ventana, image=logo, bg="#222226")  
            logo_label.place(relx=0.5, rely=0.35, anchor="center")  # Centrado un poco más arriba
        # Botón de Ventas
        boton_ventas = tk.Button(ventana, text="VENTAS", font=("Arial", 14), bg="white", fg="black", command=ventana_ventas)
        boton_ventas.place(relx=0.5, rely=0.70, anchor="center")
        
        # Botón de Insumos
        if self.getrol() == "Admin": 
            boton_insumos = tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=ventana_insumos)
            boton_insumos.place(relx=0.5, rely=0.80, anchor="center")
            boton_insumos = tk.Button(ventana, text="Adm. us", font=("Arial", 10), bg="white", fg="black", command=ventana_usuarios)
            boton_insumos.place(relx=0.1, rely=0.95, anchor="center")
        elif self.getrol() == "User":
            boton_insumos = tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=lambda:cerrar_sesion(2))
            boton_insumos.place(relx=0.5, rely=0.80, anchor="center")
        boton_ventas = tk.Button(ventana, text="CERRAR", font=("Arial", 14), bg="red", fg="black", command=lambda:cerrar_sesion(1))
        boton_ventas.place(relx=0.5, rely=0.90, anchor="center")
        ventana.mainloop()

    def abrir_inventario(self):
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
            conexion = self.obtener_conexion()
            if conexion is None:
                return 
            try:
                cursor=conexion.cursor()
                query = f'''
                SELECT i.id_insumo, i.nombre_insumo, COALESCE(v.cantidad, 0) AS cantidad
                FROM {schema}.Insumos i
                LEFT JOIN {schema}.VencInsumos v ON i.id_insumo = v.id_insumo
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
                messagebox.showerror("Error",f"Error al ejecutar la consulta: {err}")
            finally:
                conexion.close()
        # Función para manejar el evento de búsqueda
        def buscar(): #???
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
                
                conexion = self.obtener_conexion()
                if conexion is None:
                    return  
                # Eliminar de la base de datos
                try:
                    cursor = conexion.cursor()
                    cursor.execute(f"DELETE FROM {schema}.VencInsumos WHERE id_insumo = :1", (id_insumo,))
                    cursor.execute(f"DELETE FROM {schema}.Insumos WHERE id_insumo = :1", (id_insumo,))
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

        if self.getrol() == "Admin":
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
    #VENTANA DE ADMIN DE USUARIOS
    def abrir_usuarios(self):
        # Crear nueva ventana
        nueva_ventana = tk.Tk()
        nueva_ventana.title("Administrar usuarios")
        nueva_ventana.state("zoomed")

        # Etiqueta de título
        tk.Label(nueva_ventana, text="Administrar usuarios", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Crear un marco para la tabla
        frame_tabla = tk.Frame(nueva_ventana)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

        # Mostrar datos
        tree = ttk.Treeview(frame_tabla, columns=("id_usuario", "nombre_usuario", "contrasenia", "rol"), show="headings", height=20)
        tree.heading("id_usuario", text="Código del usuario")
        tree.heading("nombre_usuario", text="Nombre del usuario")
        tree.heading("contrasenia", text="Contraseña del usuario")
        tree.heading("rol", text="Rol del usuario")
        
        tree.column("id_usuario", width=300, anchor="center")
        tree.column("nombre_usuario", width=300, anchor="center")
        tree.column("contrasenia", width=300, anchor="center")
        tree.column("rol", width=150, anchor="center")

        tree.pack(side="left", fill="both", expand=True)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Configurar etiquetas de color
        tree.tag_configure('admin', foreground="blue")
        tree.tag_configure('empleado', foreground="green")

        def cargar_datos(filtro=""):
            """
            Carga los datos en el Treeview según el filtro proporcionado y aplica colores.
            """
            conexion = self.obtener_conexion()
            if conexion is None:
                return    
            try:
                cursor = conexion.cursor()
                query = f'''
                SELECT u.id_usuario, u.nombre_usuario, u.contrasenia, r.rol
                FROM {schema}.UsuariosNom u
                JOIN {schema}.UsuariosRol r ON u.id_usuario = r.id_usuario
                WHERE LOWER(u.nombre_usuario) LIKE :filtro
                '''
                cursor.execute(query, {"filtro": f"%{filtro.lower()}%"})
                
                # Limpiar la tabla antes de insertar nuevos datos
                for item in tree.get_children():
                    tree.delete(item)
                
                # Insertar datos en la tabla con colores según el rol
                resultados = cursor.fetchall()
                for fila in resultados:
                    id_usuario, nombre_usuario, contrasenia, rol = fila
                    if rol == "Admin":
                        tag = 'admin'
                    elif rol == "Emple":
                        tag = 'empleado'
                    tree.insert("", "end", values=fila, tags=(tag,))
            except Exception as err:
                messagebox.showerror("Error", f"Error al ejecutar la consulta: {err}")
            finally:
                conexion.close()
        # Función para manejar el evento de búsqueda
        def buscar():
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
                id_usuario= valores[0]  # Obtener el ID del pedido
                
                conexion = self.obtener_conexion()
                if conexion is None:
                    return  
                # Eliminar de la base de datos
                try:
                    cursor = conexion.cursor()
                    cursor.execute(f"DELETE FROM {schema}.UsuariosRol WHERE id_usuario = :1", (id_usuario,))
                    cursor.execute(f"DELETE FROM {schema}.UsuariosNom WHERE id_usuario = :1", (id_usuario,))
                    conexion.commit()

                except oracledb.DatabaseError as err:
                    messagebox.showerror("Error", f"Error al eliminar el registro: {err}")
                    return
                finally:
                    conexion.close()                
                # Eliminar la fila del Treeview
                tree.delete(seleccion)
                messagebox.showinfo("Éxito", f"Registro con ID {id_usuario} eliminado correctamente.")
            
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la fila: {e}")

        # Cargar los datos al abrir la ventana
        cargar_datos()
        #Boton para borrar registro de inventarios
        boton_eliminar = tk.Button(nueva_ventana, text="Eliminar usuario", font=("Arial", 14), command=eliminar_fila)
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
    def abrir_ventas(self):
        # Crear nueva ventana
        nueva_ventana = tk.Tk()
        nueva_ventana.title("Ventas")
        nueva_ventana.state("zoomed")
    # Función para abrir una ventana y mostrar los datos de la consulta SQ
        conexion = self.obtener_conexion()
        if conexion is None:
            return
        try:
            cursor = conexion.cursor()
            consulta = f"""
            SELECT 
                pd.id_pedido,
                pd.fecha_pedido,
                pd.hora_pedido,
                p.id_alimento,
                p.cantidad_alimento,
                p.total_pedido,
                p.direccion,
                p.nombre_cliente
            FROM {schema}.PedidoDetalles pd
            JOIN {schema}.Pedidos p ON pd.id_pedido = p.id_pedido
            """
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            # Crear una tabla para mostrar los datos
            tree = ttk.Treeview(nueva_ventana, columns=(
                "id_pedido", "fecha_pedido", "hora_pedido", "id_alimento",
                "cantidad_alimento", "total_pedido", "direccion", "nombre_cliente"
            ), show="headings", height=20)
            # Configurar encabezados
            encabezados = [
                "ID Pedido", "Fecha Pedido", "Hora Pedido", "ID Alimento",
                "Cantidad", "Total", "Dirección", "Nombre Cliente"
            ]
            for i, encabezado in enumerate(encabezados):
                tree.heading(tree["columns"][i], text=encabezado)
                tree.column(tree["columns"][i], width=100)
        # Insertar datos en la tabla
            for fila in resultados:
                tree.insert("", tk.END, values=fila)
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        except oracledb.DatabaseError as e:
            self.mostrar_error(f"Error al ejecutar la consulta: {e}")
        finally:
            if conexion:
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
                
                conexion = self.obtener_conexion()
                if conexion is None:
                    return  
                # Eliminar de la base de datos
                try:
                    cursor = conexion.cursor()
                    cursor.execute(f"DELETE FROM {schema}.PedidoDetalles WHERE id_pedido = :1", (id_pedido,))
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
        #Boton para borrar registro de ventas
        boton_eliminar = tk.Button(nueva_ventana, text="Eliminar Pedido", font=("Arial", 14), command=eliminar_fila)
        boton_eliminar.pack(pady=10)
        
        def cerrar_ventana():
            nueva_ventana.destroy()        
        # Botón para cerrar la ventana
        boton_cerrar = tk.Button(nueva_ventana, text="Cerrar", font=("Arial", 14), command=cerrar_ventana)
        boton_cerrar.pack(pady=10)
        nueva_ventana.mainloop()
if __name__ == "__main__":
    app=hanburguesa()