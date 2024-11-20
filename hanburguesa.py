import tkinter as tk
from tkinter import messagebox  # Para mostrar mensajes de error
from PIL import Image, ImageTk  # Pillow para manejar imágenes avanzadas

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Interfaz de Ventas e Insumos")
ventana.state("zoomed")
#ventana.resizable(False, False)

# Función para mostrar un mensaje de error
def mostrar_error(mensaje):
    messagebox.showerror("Error", mensaje)

# Función para abrir una nueva ventana (ejemplo)
def abrir_nueva_ventana(titulo):
    ventana.destroy()
    nueva_ventana = tk.Tk() #Se convierte en la nueva ventana principal 
    nueva_ventana.title(titulo)
    nueva_ventana.state("zoomed")
    tk.Label(nueva_ventana, text=f"Esta es la ventana de {titulo}").pack(pady=20)
    nueva_ventana.mainloop()

# Cargar el logo con Pillow (con manejo de errores)
try:
    # Abre la imagen con Pillow
    imagen_logo = Image.open("logo.png")  # Asegúrate de que el archivo existe
    imagen_logo = imagen_logo.resize((200, 200), Image.Resampling.LANCZOS)  # Redimensiona la imagen
    logo = ImageTk.PhotoImage(imagen_logo)  # Convierte la imagen a un formato compatible con Tkinter
except Exception as e:
    mostrar_error(f"No se pudo cargar el logo: {e}")
    logo = None  # Si hay error, no mostrar el logo

# Crear el widget del logo
if logo:
    logo_label = tk.Label(ventana, image=logo)
    logo_label.pack(pady=20)

# Botón de Ventas
def abrir_ventas():
    abrir_nueva_ventana("Ventas")
boton_ventas = tk.Button(ventana, text="VENTAS", font=("Arial", 14), bg="white", fg="black", command=abrir_ventas)
boton_ventas.pack(pady=20)

# Botón de Insumos
def abrir_insumos():
    abrir_nueva_ventana("Insumos")
boton_insumos = tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=abrir_insumos)
boton_insumos.pack(pady=20)

# Ejecutar el bucle de la interfaz
ventana.mainloop()