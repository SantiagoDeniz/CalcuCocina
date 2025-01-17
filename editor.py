import tkinter as tk
from tkinter import Toplevel, Scrollbar, Y, BOTH, messagebox
import csv
import os
import sys

def edit_ingredients_csv(csv_file):
    """Editar CSV de ingredientes con 4 columnas."""
    edit_csv(csv_file, "Editar Ingredientes", ["Ingrediente", "Costo", "Unidad", "Stock"])

def edit_packaging_csv(csv_file):
    """Editar CSV de materiales para packaging con 3 columnas."""
    edit_csv(csv_file, "Editar Materiales para Packaging", ["Material", "Costo", "Stock"])

def edit_csv(csv_file, title, headers):
    if not os.path.exists(csv_file):
        messagebox.showerror("Error", "No CSV file loaded to edit.")
        return

    def save_changes():
        update_rows()
        for row in rows[1:]:  # Ignore headers when checking completeness
            if not all(row):
                messagebox.showerror("Error", "All rows must be complete before saving.")
                return
        try:
            rows[0] = headers  # Ensure headers are correct
            data_rows = rows[1:]
            data_rows.sort(key=lambda x: x[0].lower())  # Sort rows alphabetically by the first column
            with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            messagebox.showinfo("Success", "CSV file updated successfully.")
            editor_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_row():
        rows.append(["" for _ in headers])
        entries.append([None for _ in headers])
        update_display()

    def delete_row():
        selected_row = listbox.curselection()
        if selected_row:
            row_index = selected_row[0]
            if row_index == 0:
                messagebox.showerror("Error", "Cannot delete the header row.")
            else:
                rows.pop(row_index)
                entries.pop(row_index)
                update_display()
        else:
            messagebox.showerror("Error", "Please select a row to delete.")

    def update_display():
        for widget in entry_frame.winfo_children():
            widget.destroy()

        listbox.delete(0, tk.END)

        for i, row in enumerate(rows):
            row_display = " | ".join(row)
            listbox.insert(tk.END, row_display)

            # Definir el color de fondo según la fila
            bg_color = "#d9ead3" if i == 0 else ("#ffffff" if i % 2 == 0 else "#fff2f2")

            entry_row = tk.Frame(entry_frame, bg=bg_color)
            entry_row.pack(fill="x", pady=2)

            entry_row_entries = []
            for col_index, value in enumerate(row):
                # Definir el ancho según la columna
                if col_index == 0:  # Primera columna (Ingrediente o Material)
                    width = 27
                elif col_index == 1:  # Segunda columna (Costo)
                    width = 10
                elif col_index == 2:  # Tercera columna (Unidad o Stock)
                    width = 9
                else:  # Columnas adicionales
                    width = 9

                # Crear entrada con propiedades específicas
                entry = tk.Entry(
                    entry_row,
                    width=width,
                    bg=bg_color,
                    fg="#333333",
                    font=("Arial", 10, "bold" if i == 0 else "normal"),
                    justify=("left" if i != 0 and col_index == 0 else "center")
                )
                entry.insert(0, value)
                entry.pack(side="left", padx=2)

                # Hacer que las celdas de encabezado sean de solo lectura
                entry.config(state="normal" if i > 0 else "readonly")
                entry_row_entries.append(entry)

            entries.append(entry_row_entries)


    def update_rows():
        for i, entry_row in enumerate(entry_frame.winfo_children()):
            rows[i] = [child.get() for child in entry_row.winfo_children() if isinstance(child, tk.Entry)]

    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            rows = [row for row in csv.reader(file)]
            if not rows or rows[0] != headers:  # Ensure correct headers
                rows.insert(0, headers)
            entries = []

        editor_window = Toplevel()
        editor_window.title(title)
        editor_window.geometry("900x450")
        editor_window.configure(bg="#b6d7a8")

        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, "assets/icono.ico")
            else:
                icon_path = "assets/icono.ico"

            editor_window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

        # Frames for columns
        left_column = tk.Frame(editor_window, bg="#b6d7a8", width=450)
        left_column.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_column = tk.Frame(editor_window, bg="#b6d7a8", width=450)
        right_column.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Left column: Edit rows
        tk.Label(left_column, text=title, bg="#d9ead3", fg="#333333", font=("Arial", 14)).pack(pady=10)

        left_canvas = tk.Canvas(left_column, bg="#d9ead3")
        left_scrollbar = Scrollbar(left_column, orient="vertical", command=left_canvas.yview)
        left_scrollbar.pack(side="right", fill="y")
        left_canvas.pack(side="left", fill="both", expand=True)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        entry_frame = tk.Frame(left_canvas, bg="#d9ead3")
        left_canvas.create_window((0, 0), window=entry_frame, anchor="nw")

        def resize_canvas(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        entry_frame.bind("<Configure>", resize_canvas)

        def scroll_left_canvas(event):
            left_canvas.yview_scroll(-1 * (event.delta // 120), "units")

        left_canvas.bind("<Enter>", lambda _: left_canvas.bind_all("<MouseWheel>", scroll_left_canvas))
        left_canvas.bind("<Leave>", lambda _: left_canvas.unbind_all("<MouseWheel>"))

        # Right column: Listbox and buttons
        tk.Label(right_column, text="Seleccionar Fila", bg="#d9ead3", fg="#333333", font=("Arial", 14)).pack(pady=5)

        listbox_frame = tk.Frame(right_column, bg="#d9ead3")
        listbox_frame.pack(fill="both", expand=True, pady=10)

        listbox_scrollbar = Scrollbar(listbox_frame, orient="vertical")
        listbox_scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(listbox_frame, height=10, width=50, bg="#ffffff", fg="#333333", font=("Arial", 10), yscrollcommand=listbox_scrollbar.set)
        listbox.pack(fill="both", padx=10, pady=10)
        listbox_scrollbar.config(command=listbox.yview)

        def scroll_listbox(event):
            listbox.yview_scroll(-1 * (event.delta // 120), "units")

        listbox.bind("<Enter>", lambda _: listbox.bind_all("<MouseWheel>", scroll_listbox))
        listbox.bind("<Leave>", lambda _: listbox.unbind_all("<MouseWheel>"))

        button_frame = tk.Frame(right_column, bg="#b6d7a8")
        button_frame.pack(fill="x", pady=20)

        tk.Button(button_frame, text="Agregar Nueva Fila", command=add_row, bg="#9fc5e8", fg="#333333", font=("Arial", 10)).pack(fill="x", padx=20, pady=5)
        tk.Button(button_frame, text="Eliminar Fila Seleccionada", command=delete_row, bg="#9fc5e8", fg="#333333", font=("Arial", 10)).pack(fill="x", padx=20, pady=5)
        tk.Button(button_frame, text="Guardar Cambios", command=save_changes, bg="#6fa8dc", fg="#ffffff", font=("Arial", 12, "bold")).pack(fill="x", padx=20, pady=10)

        update_display()

    except Exception as e:
        messagebox.showerror("Error", str(e))
