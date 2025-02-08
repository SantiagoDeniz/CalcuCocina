import tkinter as tk
from tkinter import PhotoImage, messagebox
import os
import sys
from logic import calculate_with_ai, consume_stock_logic
from utils import load_last_csv, save_last_csv, select_and_save_csv
from editor import edit_ingredients_csv, edit_packaging_csv
import state

def create_button(parent, text, command, bg="#f4cccc", fg="#333333", font=("Arial", 9), **kwargs):
    """
    Crea un botón con estilo estándar.

    Args:
        parent (tk.Widget): El widget padre donde se colocará el botón.
        text (str): El texto que mostrará el botón.
        command (callable): La función que se ejecutará al hacer clic.
        bg (str): Color de fondo del botón (opcional, por defecto #f4cccc).
        fg (str): Color del texto del botón (opcional, por defecto #333333).
        font (tuple): Fuente del texto (opcional, por defecto Arial, tamaño 9).
        **kwargs: Argumentos adicionales que se pasan al constructor de `tk.Button`.

    Returns:
        tk.Button: El botón creado.
    """
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, font=font, **kwargs)

def create_main_window(root):
    root.configure(bg="#cce7e8")  # Light mint background for main window

    # Frames
    left_frame = tk.Frame(root, bg="#e8f4f8")
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = tk.Frame(root, bg="#e8f4f8")
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    ''''''

    # File selection for ingredients
    def create_csv_loader(parent_frame, title, variable, file_type, edit_command):
        """
        Crea un conjunto de widgets para cargar y editar un archivo CSV.

        Args:
            parent_frame (tk.Frame): El frame donde se colocarán los widgets.
            title (str): El título del conjunto de widgets.
            variable (tk.StringVar): La variable vinculada al campo de entrada.
            file_type (str): El tipo de archivo CSV ("ingredients" o "packaging").
            edit_command (callable): La función a ejecutar para editar el archivo CSV.
        """
        frame = tk.Frame(parent_frame, bg="#e8f4f8")
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text=title, bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)

        last_csv = load_last_csv(file_type)
        if last_csv and os.path.exists(last_csv):
            variable.set(last_csv)

        def select_file():
            path = select_and_save_csv(file_type)
            if path:
                variable.set(path)

        tk.Entry(frame, textvariable=variable, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9)).pack(pady=5)

        buttons_frame = tk.Frame(frame, bg="#e8f4f8")
        buttons_frame.pack(pady=3)

        create_button(buttons_frame, text="Seleccionar Archivo", command=select_file).pack(side="left", padx=5)
        create_button(buttons_frame, text="Editar Archivo", command=edit_command).pack(side="left", padx=5)

    # Carga de ingredientes
    ingredients_csv_path = tk.StringVar()
    create_csv_loader(
        parent_frame=left_frame,
        title="Sube tu archivo CSV con ingredientes y costos:",
        variable=ingredients_csv_path,
        file_type="ingredients",
        edit_command=lambda: edit_ingredients_csv(ingredients_csv_path.get())
    )

    tk.Label(left_frame, text="Ingresa los ingredientes y cantidades de la receta:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)
    recipe_text = tk.Text(left_frame, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    recipe_text.pack(pady=3)

    # Empty section for spacing
    tk.Frame(left_frame, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Carga de materiales para packaging
    packaging_csv_path = tk.StringVar()
    create_csv_loader(
        parent_frame=left_frame,
        title="Sube tu archivo CSV con materiales para packaging:",
        variable=packaging_csv_path,
        file_type="packaging",
        edit_command=lambda: edit_packaging_csv(packaging_csv_path.get())
    )

    tk.Label(left_frame, text="Ingresa los materiales y cantidades para el packaging:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=3)
    packaging_text = tk.Text(left_frame, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    packaging_text.pack(pady=3)

    # Empty section for spacing
    tk.Frame(left_frame, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Frame for fixed costs, labor hours, and profit margin
    others_frame = tk.Frame(left_frame, bg="#e8f4f8")
    others_frame.pack(fill="x", pady=10)

    fixed_labor_profit_frame = tk.Frame(others_frame, bg="#e8f4f8")
    fixed_labor_profit_frame.pack()

    # Fixed costs, labor hours, and profit margin aligned horizontally
    combined_frame = tk.Frame(fixed_labor_profit_frame, bg="#e8f4f8")
    combined_frame.pack(anchor="center", pady=5)

    # Fixed costs input
    fixed_costs_frame = tk.Frame(combined_frame, bg="#e8f4f8")
    fixed_costs_frame.pack(side="left", padx=10)
    tk.Label(fixed_costs_frame, text="Gastos fijos ($):", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    fixed_costs_entry = tk.Entry(fixed_costs_frame, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    fixed_costs_entry.insert(0, "50")  # Default value
    fixed_costs_entry.pack()

    # Labor hours input
    labor_hours_frame = tk.Frame(combined_frame, bg="#e8f4f8")
    labor_hours_frame.pack(side="left", padx=10)
    tk.Label(labor_hours_frame, text="Horas de trabajo:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    labor_hours_entry = tk.Entry(labor_hours_frame, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    labor_hours_entry.insert(0, "1.5")  # Default value
    labor_hours_entry.pack()

    # Profit margin input
    profit_margin_frame = tk.Frame(combined_frame, bg="#e8f4f8")
    profit_margin_frame.pack(side="left", padx=10)
    tk.Label(profit_margin_frame, text="Porcentaje de ganancia (%):", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    profit_percentage = tk.Entry(profit_margin_frame, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    profit_percentage.insert(0, "35")  # Default value
    profit_percentage.pack()

    # Calculate button
    create_button(
    others_frame,
    text="Calcular con IA",
    command=lambda: calculate_with_ai(
        ingredients_csv_path.get(),
        recipe_text.get("1.0", tk.END).strip(),
        packaging_csv_path.get(),
        packaging_text.get("1.0", tk.END).strip(),
        fixed_costs_entry.get().strip(),
        labor_hours_entry.get().strip(),
        profit_percentage.get().strip(),
        result_text
    ),
    bg="#4caf80",
    fg="#ffffff",
    font=("Arial", 12)
).pack(pady=10)


    # Load CSV content automatically if last CSV exists
    last_csv = load_last_csv("ingredients")
    if last_csv and os.path.exists(last_csv):
        save_last_csv(ingredients_csv_path.get(), "ingredients")

    last_csv = load_last_csv("packaging")
    if last_csv and os.path.exists(last_csv):
        save_last_csv(packaging_csv_path.get(), "packaging")

    #Add logo
    try:
        logo_path = os.path.join(sys._MEIPASS, "assets/logo.png") if hasattr(sys, '_MEIPASS') else "assets/logo.png"

        logo_image = PhotoImage(file=logo_path).subsample(6, 6)
        logo_label = tk.Label(right_frame, image=logo_image, bg="#e8f4f8")
        logo_label.image = logo_image
        logo_label.pack(pady=7)
    except Exception as e:
        tk.Label(right_frame, text=f"[Logo no encontrado: {e}]", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=10)

    # Result display
    tk.Label(right_frame, text="Resultado:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=3)
    result_text = tk.StringVar()
    result_display = tk.Text(right_frame, height=25, width=50, wrap="word", bg="#ffffff", fg="#333333", font=("Arial", 9))
    result_display.pack(pady=2, padx=5)

    def update_result():
        result_display.delete("1.0", tk.END)
        result_display.insert(tk.END, result_text.get())

    result_text.trace("w", lambda *args: update_result())

    def consume_stock():
        if not state.hidden_parts_global:
            messagebox.showerror("Error", "No hay datos disponibles para consumir el stock.")
            return
        try:
            consume_stock_logic(
                state.hidden_parts_global,  # Usar las partes ocultas de la respuesta
                ingredients_csv_path.get(),
                packaging_csv_path.get()
            )
            messagebox.showinfo("Éxito", "El stock se actualizó correctamente.")
        except Exception as e:
            messagebox.showerror("Error",  f"No se pudo actualizar el stock: {e}")


    # Botón "Consumir Stock"
    create_button(
        right_frame,
        text="Consumir Stock",
        command=consume_stock,
        bg="#fff2f2",
        font=("Arial", 9)
    ).pack(pady=10)

