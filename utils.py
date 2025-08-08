def load_last_csv(file_type):
    """
    Load the path of the last CSV file based on the given type (e.g., 'ingredients' or 'packaging').
    """
    file_name = f"last_{file_type}_csv.txt"
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            return file.read().strip()
    return ""

def save_last_csv(path, file_type):
    """
    Save the path of the last CSV file based on the given type (e.g., 'ingredients' or 'packaging').
    """
    file_name = f"last_{file_type}_csv.txt"
    with open(file_name, "w") as file:
        file.write(path)

def select_and_save_csv(type):
    path = filedialog.askopenfilename()
    if path:
        save_last_csv(path, type)
        return path
    return None
import os
from tkinter import filedialog

def cargar_ultimo_csv(tipo: str) -> str:
    """
    Carga la ruta del último archivo CSV usado para el tipo dado ('ingredients' o 'packaging').
    """
    nombre_archivo = f"last_{tipo}_csv.txt"
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            return archivo.read().strip()
    return ""

def guardar_ultimo_csv(ruta: str, tipo: str) -> None:
    """
    Guarda la ruta del último archivo CSV usado para el tipo dado ('ingredients' o 'packaging').
    """
    nombre_archivo = f"last_{tipo}_csv.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(ruta)

def seleccionar_y_guardar_csv(tipo: str) -> str | None:
    """
    Abre un diálogo para seleccionar un archivo CSV y guarda la ruta seleccionada.
    """
    ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
    if ruta:
        guardar_ultimo_csv(ruta, tipo)
        return ruta
    return None
