import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ventas import abrir_ventas  # Importa la función desde ventas.py

# Crear la ventana principal
def main():
    ventana = tk.Tk()
    ventana.title("Interfaz de Ventas e Insumos")
    ventana.state("zoomed")

    # Logo
    try:
        imagen_logo = Image.open("logo.png")
        imagen_logo = imagen_logo.resize((300, 300), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(imagen_logo)
        logo_label = tk.Label(ventana, image=logo)
        logo_label.image = logo
        logo_label.pack(pady=20)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el logo: {e}")

    # Botones
    tk.Button(ventana, text="VENTAS", font=("Arial", 14), bg="white", fg="black", command=abrir_ventas).pack(pady=20)
    tk.Button(ventana, text="INSUMOS", font=("Arial", 14), bg="black", fg="white", command=lambda: messagebox.showinfo("Insumos", "Proximamente")).pack(pady=20)

    ventana.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
