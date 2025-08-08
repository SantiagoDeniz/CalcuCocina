import tkinter as tk
from tkinter import PhotoImage, messagebox
import os
import sys
from logic import calcular_con_ia, consumir_stock_logica
from utils import cargar_ultimo_csv, guardar_ultimo_csv, seleccionar_y_guardar_csv
from editor import editar_csv_ingredientes, editar_csv_packaging
import state

def crear_boton(padre, texto, comando, bg="#f4cccc", fg="#333333", font=("Arial", 9), **kwargs):
    """
    Crea un botón con estilo estándar.
    """
    return tk.Button(padre, text=texto, command=comando, bg=bg, fg=fg, font=font, **kwargs)

def crear_ventana_principal(raiz):
    """
    Crea la ventana principal de la aplicación CalcuCocina.
    """
    raiz.configure(bg="#cce7e8")

    # Frames
    marco_izquierdo = tk.Frame(raiz, bg="#e8f4f8")
    marco_izquierdo.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    marco_derecho = tk.Frame(raiz, bg="#e8f4f8")
    marco_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def crear_cargador_csv(marco_padre, titulo, variable, tipo_archivo, comando_editar):
        """
        Crea widgets para cargar y editar un archivo CSV.
        """
        frame = tk.Frame(marco_padre, bg="#e8f4f8")
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text=titulo, bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)

        ultimo_csv = cargar_ultimo_csv(tipo_archivo)
        if ultimo_csv and os.path.exists(ultimo_csv):
            variable.set(ultimo_csv)

        def seleccionar_archivo():
            ruta = seleccionar_y_guardar_csv(tipo_archivo)
            if ruta:
                variable.set(ruta)

        tk.Entry(frame, textvariable=variable, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9)).pack(pady=5)

        marco_botones = tk.Frame(frame, bg="#e8f4f8")
        marco_botones.pack(pady=3)

        crear_boton(marco_botones, texto="Seleccionar Archivo", comando=seleccionar_archivo).pack(side="left", padx=5)
        crear_boton(marco_botones, texto="Editar Archivo", comando=comando_editar).pack(side="left", padx=5)

    # Carga de ingredientes
    ruta_csv_ingredientes = tk.StringVar()
    crear_cargador_csv(
        marco_padre=marco_izquierdo,
        titulo="Sube tu archivo CSV con ingredientes y costos:",
        variable=ruta_csv_ingredientes,
        tipo_archivo="ingredients",
        comando_editar=lambda: editar_csv_ingredientes(ruta_csv_ingredientes.get())
    )

    tk.Label(marco_izquierdo, text="Ingresa los ingredientes y cantidades de la receta:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack(pady=3)
    texto_receta = tk.Text(marco_izquierdo, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    texto_receta.pack(pady=3)

    tk.Frame(marco_izquierdo, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Carga de materiales para packaging
    ruta_csv_packaging = tk.StringVar()
    crear_cargador_csv(
        marco_padre=marco_izquierdo,
        titulo="Sube tu archivo CSV con materiales para packaging:",
        variable=ruta_csv_packaging,
        tipo_archivo="packaging",
        comando_editar=lambda: editar_csv_packaging(ruta_csv_packaging.get())
    )

    tk.Label(marco_izquierdo, text="Ingresa los materiales y cantidades para el packaging:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=3)
    texto_packaging = tk.Text(marco_izquierdo, height=5, width=50, bg="#ffffff", fg="#333333", font=("Arial", 9))
    texto_packaging.pack(pady=3)

    tk.Frame(marco_izquierdo, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Frame para gastos fijos, horas de trabajo y ganancia
    marco_otros = tk.Frame(marco_izquierdo, bg="#e8f4f8")
    marco_otros.pack(fill="x", pady=10)

    marco_gastos_labor_ganancia = tk.Frame(marco_otros, bg="#e8f4f8")
    marco_gastos_labor_ganancia.pack()

    marco_combinado = tk.Frame(marco_gastos_labor_ganancia, bg="#e8f4f8")
    marco_combinado.pack(anchor="center", pady=5)

    # Gastos fijos
    marco_gastos = tk.Frame(marco_combinado, bg="#e8f4f8")
    marco_gastos.pack(side="left", padx=10)
    tk.Label(marco_gastos, text="Gastos fijos ($):", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    entrada_gastos = tk.Entry(marco_gastos, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    entrada_gastos.insert(0, "50")
    entrada_gastos.pack()

    # Horas de trabajo
    marco_labor = tk.Frame(marco_combinado, bg="#e8f4f8")
    marco_labor.pack(side="left", padx=10)
    tk.Label(marco_labor, text="Horas de trabajo:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    entrada_labor = tk.Entry(marco_labor, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    entrada_labor.insert(0, "1.5")
    entrada_labor.pack()

    # Porcentaje de ganancia
    marco_ganancia = tk.Frame(marco_combinado, bg="#e8f4f8")
    marco_ganancia.pack(side="left", padx=10)
    tk.Label(marco_ganancia, text="Porcentaje de ganancia (%):", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    entrada_ganancia = tk.Entry(marco_ganancia, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    entrada_ganancia.insert(0, "35")
    entrada_ganancia.pack()

    # Validación de entradas numéricas
    def validar_entradas_numericas():
        try:
            float(entrada_gastos.get().strip())
            float(entrada_labor.get().strip())
            float(entrada_ganancia.get().strip())
            return True
        except ValueError:
            return False

    # Botón Calcular con IA
    crear_boton(
        marco_otros,
        texto="Calcular con IA",
        comando=lambda: calcular_con_ia(
            ruta_csv_ingredientes.get(),
            texto_receta.get("1.0", tk.END).strip(),
            ruta_csv_packaging.get(),
            texto_packaging.get("1.0", tk.END).strip(),
            entrada_gastos.get().strip(),
            entrada_labor.get().strip(),
            entrada_ganancia.get().strip(),
            texto_resultado
        ) if validar_entradas_numericas() else messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos en gastos, horas y ganancia."),
        bg="#4caf80",
        fg="#ffffff",
        font=("Arial", 12)
    ).pack(pady=10)

    # Cargar CSV automáticamente si existe
    ultimo_csv = cargar_ultimo_csv("ingredients")
    if ultimo_csv and os.path.exists(ultimo_csv):
        guardar_ultimo_csv(ruta_csv_ingredientes.get(), "ingredients")

    ultimo_csv = cargar_ultimo_csv("packaging")
    if ultimo_csv and os.path.exists(ultimo_csv):
        guardar_ultimo_csv(ruta_csv_packaging.get(), "packaging")

    # Logo
    try:
        ruta_logo = os.path.join(sys._MEIPASS, "assets/logo.png") if hasattr(sys, '_MEIPASS') else "assets/logo.png"
        logo_img = PhotoImage(file=ruta_logo).subsample(6, 6)
        etiqueta_logo = tk.Label(marco_derecho, image=logo_img, bg="#e8f4f8")
        etiqueta_logo.image = logo_img
        etiqueta_logo.pack(pady=7)
    except Exception as e:
        tk.Label(marco_derecho, text=f"[Logo no encontrado: {e}]", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=10)

    # Resultado
    tk.Label(marco_derecho, text="Resultado:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=3)
    texto_resultado = tk.StringVar()
    display_resultado = tk.Text(marco_derecho, height=25, width=50, wrap="word", bg="#ffffff", fg="#333333", font=("Arial", 9))
    display_resultado.pack(pady=2, padx=5)

    def actualizar_resultado():
        display_resultado.delete("1.0", tk.END)
        display_resultado.insert(tk.END, texto_resultado.get())

    texto_resultado.trace("w", lambda *args: actualizar_resultado())

    def consumir_stock():
        if not state.hidden_parts_global:
            messagebox.showerror("Error", "No hay datos disponibles para consumir el stock.")
            return
        try:
            consumir_stock_logica(
                state.hidden_parts_global,
                ruta_csv_ingredientes.get(),
                ruta_csv_packaging.get()
            )
            messagebox.showinfo("Éxito", "El stock se actualizó correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el stock: {e}")

    # Botón Consumir Stock
    crear_boton(
        marco_derecho,
        texto="Consumir Stock",
        comando=consumir_stock,
        bg="#fff2f2",
        font=("Arial", 9)
    ).pack(pady=10)

