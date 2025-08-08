
import tkinter as tk
import os
import sys
from gui import crear_ventana_principal

if __name__ == "__main__":
    root = tk.Tk()
    root.title("CalcuCocina")
    root.geometry("800x600")
    root.configure(bg="#f7f7f7")

    # Manejo de rutas para PyInstaller
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "assets/icono.ico")
    else:
        icon_path = "assets/icono.ico"

    try:
        root.iconbitmap(icon_path)
    except Exception as e:
        print(f"Error al cargar el icono: {e}")

    crear_ventana_principal(root)
    root.mainloop()
