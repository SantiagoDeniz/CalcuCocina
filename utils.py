import os
from tkinter import filedialog 

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
