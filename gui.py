import tkinter as tk
from tkinter import PhotoImage, messagebox
import os
import sys
from logic import calculate_with_ai, consume_stock_logic
from utils import load_last_csv, save_last_csv, select_and_save_csv
from editor import edit_ingredients_csv, edit_packaging_csv
import state


def create_main_window(root):
    root.configure(bg="#cce7e8")  # Light mint background for main window

    # Frames
    left_frame = tk.Frame(root, bg="#e8f4f8")  # Pastel blue for left frame
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = tk.Frame(root, bg="#e8f4f8")  # Pastel blue for right frame
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Add logo
    try:
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, "assets/logo.png")
        else:
            logo_path = "assets/logo.png"

        logo_image = PhotoImage(file=logo_path)
        logo_image = logo_image.subsample(6, 6)
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

    # File selection for ingredients
    ingredients_frame = tk.Frame(left_frame, bg="#e8f4f8")
    ingredients_frame.pack(fill="x", pady=5)

    tk.Label(ingredients_frame, text="Sube tu archivo CSV con ingredientes y costos:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)
    ingredients_csv_path = tk.StringVar()
    last_csv = load_last_csv("ingredients")
    if last_csv and os.path.exists(last_csv):
        ingredients_csv_path.set(last_csv)

    def select_ingredients_file():
        path = select_and_save_csv("ingredients")
        if path:
            ingredients_csv_path.set(path)

    tk.Entry(ingredients_frame, textvariable=ingredients_csv_path, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9)).pack(pady=5)
    file_buttons_frame = tk.Frame(ingredients_frame, bg="#e8f4f8")
    file_buttons_frame.pack(pady=3)

    tk.Button(file_buttons_frame, text="Seleccionar Archivo", command=select_ingredients_file, bg="#f4cccc", fg="#333333", font=("Arial", 9)).pack(side="left", padx=5)
    tk.Button(file_buttons_frame, text="Editar Archivo", command=lambda: edit_ingredients_csv(ingredients_csv_path.get()), bg="#f4cccc", fg="#333333", font=("Arial", 9)).pack(side="left", padx=5)

    tk.Label(ingredients_frame, text="Ingresa los ingredientes y cantidades del postre:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)
    recipe_text = tk.Text(ingredients_frame, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    recipe_text.pack(pady=3)

    # Empty section for spacing
    tk.Frame(left_frame, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # File selection for packaging
    packaging_frame = tk.Frame(left_frame, bg="#e8f4f8")
    packaging_frame.pack(fill="x", pady=5)

    tk.Label(packaging_frame, text="Sube tu archivo CSV con materiales para packaging:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)
    packaging_csv_path = tk.StringVar()
    last_packaging_csv = load_last_csv("packaging")
    if last_packaging_csv and os.path.exists(last_packaging_csv):
        packaging_csv_path.set(last_packaging_csv)

    def select_packaging_file():
        path = select_and_save_csv("packaging")
        if path:
            packaging_csv_path.set(path)

    tk.Entry(packaging_frame, textvariable=packaging_csv_path, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9)).pack(pady=5)
    packaging_buttons_frame = tk.Frame(packaging_frame, bg="#e8f4f8")
    packaging_buttons_frame.pack(pady=3)

    tk.Button(packaging_buttons_frame, text="Seleccionar Archivo", command=select_packaging_file, bg="#f4cccc", fg="#333333", font=("Arial", 9)).pack(side="left", padx=5)
    tk.Button(packaging_buttons_frame, text="Editar Archivo", command=lambda: edit_packaging_csv(packaging_csv_path.get()), bg="#f4cccc", fg="#333333", font=("Arial", 9)).pack(side="left", padx=5)

    tk.Label(packaging_frame, text="Ingresa los materiales y cantidades para el packaging:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=5)
    packaging_text = tk.Text(packaging_frame, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    packaging_text.pack(pady=5)

    # Empty section for spacing
    tk.Frame(left_frame, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Frame for fixed costs, labor hours, and profit margin
    others_frame = tk.Frame(left_frame, bg="#e8f4f8")
    others_frame.pack(fill="x", pady=10)

    labor_profit_frame = tk.Frame(others_frame, bg="#e8f4f8")
    labor_profit_frame.pack()

    # Fixed costs, labor hours, and profit margin aligned horizontally
    combined_frame = tk.Frame(labor_profit_frame, bg="#e8f4f8")
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
    tk.Button(others_frame, text="Calcular con IA", command=lambda: calculate_with_ai(
        ingredients_csv_path.get(),
        recipe_text.get("1.0", tk.END).strip(),
        packaging_csv_path.get(),
        packaging_text.get("1.0", tk.END).strip(),
        fixed_costs_entry.get().strip(),
        labor_hours_entry.get().strip(),
        profit_percentage.get().strip(),
        result_text
    ), bg="#4caf80", fg="#ffffff", font=("Arial", 12)).pack(pady=10)

    # Load CSV content automatically if last CSV exists
    if last_csv and os.path.exists(last_csv):
        save_last_csv(ingredients_csv_path.get(), "ingredients")

    if last_packaging_csv and os.path.exists(last_packaging_csv):
        save_last_csv(packaging_csv_path.get(), "packaging")

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
                messagebox.showerror("Error", f"No se pudo actualizar el stock: {e}")

        # Botón "Consumir Stock"
    tk.Button(
        right_frame,
        text="Consumir Stock",
        command=consume_stock,
        bg="#fff2f2",
        fg="#333333",
        font=("Arial", 9)
    ).pack(pady=10)