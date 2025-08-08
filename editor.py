import tkinter as tk
from tkinter import Toplevel, Scrollbar, Y, BOTH, messagebox
import csv
import os
import sys



def editar_csv_ingredientes(ruta_csv):
    """
    Edita un archivo CSV de ingredientes con 4 columnas.
    """
    editar_csv(ruta_csv, "Editar Ingredientes", ["Ingrediente", "Costo", "Unidad", "Stock"])

def editar_csv_packaging(ruta_csv):
    """
    Edita un archivo CSV de materiales para packaging con 3 columnas.
    """
    editar_csv(ruta_csv, "Editar Materiales para Packaging", ["Material", "Costo", "Stock"])


def editar_csv(ruta_csv, titulo, encabezados):
    if not os.path.exists(ruta_csv):
        messagebox.showerror("Error", "No se ha cargado un archivo CSV para editar.")
        return

    def guardar_cambios():
        actualizar_filas()
        for fila in filas[1:]:
            if not all(fila):
                messagebox.showerror("Error", "Todas las filas deben estar completas antes de guardar.")
                return
        try:
            filas[0] = encabezados
            filas_datos = filas[1:]
            filas_datos.sort(key=lambda x: x[0].lower())
            with open(ruta_csv, mode='w', encoding='utf-8', newline='') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerows(filas)
            messagebox.showinfo("Éxito", "Archivo CSV actualizado correctamente.")
            ventana_editor.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def agregar_fila():
        filas.append(["" for _ in encabezados])
        entradas.append([None for _ in encabezados])
        actualizar_display()

    def eliminar_fila():
        fila_seleccionada = listbox.curselection()
        if fila_seleccionada:
            idx = fila_seleccionada[0]
            if idx == 0:
                messagebox.showerror("Error", "No se puede eliminar la fila de encabezado.")
            else:
                filas.pop(idx)
                entradas.pop(idx)
                actualizar_display()
        else:
            messagebox.showerror("Error", "Por favor selecciona una fila para eliminar.")

    def actualizar_display():
        for widget in frame_entradas.winfo_children():
            widget.destroy()

        listbox.delete(0, tk.END)

        for i, fila in enumerate(filas):
            fila_display = " | ".join(fila)
            listbox.insert(tk.END, fila_display)

            bg_color = "#d9ead3" if i == 0 else ("#ffffff" if i % 2 == 0 else "#fff2f2")

            fila_frame = tk.Frame(frame_entradas, bg=bg_color)
            fila_frame.pack(fill="x", pady=2)

            fila_entradas = []
            for col_idx, valor in enumerate(fila):
                if col_idx == 0:
                    width = 27
                elif col_idx == 1:
                    width = 10
                elif col_idx == 2:
                    width = 9
                else:
                    width = 9
                entry = tk.Entry(
                    fila_frame,
                    width=width,
                    bg=bg_color,
                    fg="#333333",
                    font=("Arial", 10, "bold" if i == 0 else "normal"),
                    justify=("left" if i != 0 and col_idx == 0 else "center")
                )
                entry.insert(0, valor)
                entry.pack(side="left", padx=2)
                entry.config(state="normal" if i > 0 else "readonly")
                fila_entradas.append(entry)
            entradas.append(fila_entradas)

    def actualizar_filas():
        for i, fila_frame in enumerate(frame_entradas.winfo_children()):
            filas[i] = [child.get() for child in fila_frame.winfo_children() if isinstance(child, tk.Entry)]


    try:
        with open(ruta_csv, mode='r', encoding='utf-8') as archivo:
            filas = [row for row in csv.reader(archivo)]
            if not filas or filas[0] != encabezados:
                filas.insert(0, encabezados)
        entradas = []

        ventana_editor = Toplevel()
        ventana_editor.title(titulo)
        ventana_editor.geometry("900x450")
        ventana_editor.configure(bg="#b6d7a8")

        try:
            if hasattr(sys, '_MEIPASS'):
                icono_path = os.path.join(sys._MEIPASS, "assets/icono.ico")
            else:
                icono_path = "assets/icono.ico"
            ventana_editor.iconbitmap(icono_path)
        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

        columna_izq = tk.Frame(ventana_editor, bg="#b6d7a8", width=450)
        columna_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        columna_der = tk.Frame(ventana_editor, bg="#b6d7a8", width=450)
        columna_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(columna_izq, text=titulo, bg="#d9ead3", fg="#333333", font=("Arial", 14)).pack(pady=10)

        canvas_izq = tk.Canvas(columna_izq, bg="#d9ead3")
        scrollbar_izq = Scrollbar(columna_izq, orient="vertical", command=canvas_izq.yview)
        scrollbar_izq.pack(side="right", fill="y")
        canvas_izq.pack(side="left", fill="both", expand=True)
        canvas_izq.configure(yscrollcommand=scrollbar_izq.set)

        frame_entradas = tk.Frame(canvas_izq, bg="#d9ead3")
        canvas_izq.create_window((0, 0), window=frame_entradas, anchor="nw")

        def resize_canvas(event):
            canvas_izq.configure(scrollregion=canvas_izq.bbox("all"))

        frame_entradas.bind("<Configure>", resize_canvas)

        def scroll_canvas_izq(event):
            canvas_izq.yview_scroll(-1 * (event.delta // 120), "units")

        canvas_izq.bind("<Enter>", lambda _: canvas_izq.bind_all("<MouseWheel>", scroll_canvas_izq))
        canvas_izq.bind("<Leave>", lambda _: canvas_izq.unbind_all("<MouseWheel>"))

        tk.Label(columna_der, text="Seleccionar Fila", bg="#d9ead3", fg="#333333", font=("Arial", 14)).pack(pady=5)

        frame_listbox = tk.Frame(columna_der, bg="#d9ead3")
        frame_listbox.pack(fill="both", expand=True, pady=10)

        scrollbar_listbox = Scrollbar(frame_listbox, orient="vertical")
        scrollbar_listbox.pack(side="right", fill="y")

        listbox = tk.Listbox(frame_listbox, height=10, width=50, bg="#ffffff", fg="#333333", font=("Arial", 10), yscrollcommand=scrollbar_listbox.set)
        listbox.pack(fill="both", padx=10, pady=10)
        scrollbar_listbox.config(command=listbox.yview)

        def scroll_listbox(event):
            listbox.yview_scroll(-1 * (event.delta // 120), "units")

        listbox.bind("<Enter>", lambda _: listbox.bind_all("<MouseWheel>", scroll_listbox))
        listbox.bind("<Leave>", lambda _: listbox.unbind_all("<MouseWheel>"))

        frame_botones = tk.Frame(columna_der, bg="#b6d7a8")
        frame_botones.pack(fill="x", pady=20)

        tk.Button(frame_botones, text="Agregar Nueva Fila", command=agregar_fila, bg="#9fc5e8", fg="#333333", font=("Arial", 10)).pack(fill="x", padx=20, pady=5)
        tk.Button(frame_botones, text="Eliminar Fila Seleccionada", command=eliminar_fila, bg="#9fc5e8", fg="#333333", font=("Arial", 10)).pack(fill="x", padx=20, pady=5)
        tk.Button(frame_botones, text="Guardar Cambios", command=guardar_cambios, bg="#6fa8dc", fg="#ffffff", font=("Arial", 12, "bold")).pack(fill="x", padx=20, pady=10)

        actualizar_display()

    except Exception as e:
        messagebox.showerror("Error", str(e))
