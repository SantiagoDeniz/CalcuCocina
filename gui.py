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
    return tk.Button(padre, text=texto, command=comando, bg=bg, fg=fg, font=font, activebackground="#b6d7a8", activeforeground="#222222", cursor="hand2", **kwargs)
    btn = tk.Button(padre, text=texto, command=comando, bg=bg, fg=fg, font=font, activebackground="#b6d7a8", activeforeground="#222222", cursor="hand2", **kwargs)
    def on_enter(e):
        btn['bg'] = '#b6d7a8'
    def on_leave(e):
        btn['bg'] = bg
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def crear_ventana_principal(raiz):
    """
    Crea la ventana principal de la aplicación CalcuCocina.
    """
    raiz.configure(bg="#cce7e8")

    # Frames
    marco_izquierdo = tk.Frame(raiz, bg="#e8f4f8")
    marco_izquierdo.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    raiz.option_add("*Font", "Segoe UI 10")
    raiz.minsize(950, 650)

    # Área de ayuda rápida
    ayuda_frame = tk.Frame(raiz, bg="#e3f0fa", bd=2, relief="groove")
    ayuda_frame.pack(side="top", fill="x", padx=10, pady=7)
    tk.Label(ayuda_frame, text="Bienvenido a CalcuCocina", bg="#e3f0fa", fg="#1a5276", font=("Segoe UI", 15, "bold")).pack(side="left", padx=10)
    tk.Label(ayuda_frame, text="1. Sube tus archivos CSV de ingredientes y packaging. 2. Escribe tu receta y materiales. 3. Completa gastos, horas y ganancia. 4. Haz clic en 'Calcular con IA'. 5. Usa 'Consumir Stock' para actualizar inventario.", bg="#e3f0fa", fg="#333333", font=("Segoe UI", 10)).pack(side="left", padx=20)

    marco_derecho = tk.Frame(raiz, bg="#e8f4f8")
    marco_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def crear_cargador_csv(marco_padre, titulo, variable, tipo_archivo, comando_editar, tooltip_text=None):
        """
        Crea widgets para cargar y editar un archivo CSV.
        """
        frame = tk.Frame(marco_padre, bg="#e8f4f8")
        frame.pack(fill="x", pady=5)

        label = tk.Label(frame, text=titulo, bg="#e8f4f8", fg="#1a5276", font=("Segoe UI", 11, "bold"))
        label.pack(pady=3)
        if tooltip_text:
            def show_tip(event):
                tip = tk.Toplevel()
                tip.wm_overrideredirect(True)
                tip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tk.Label(tip, text=tooltip_text, bg="#fafdff", fg="#333333", relief="solid", borderwidth=1, font=("Segoe UI", 9)).pack()
                label._tipwindow = tip
            def hide_tip(event):
                if hasattr(label, '_tipwindow') and label._tipwindow:
                    label._tipwindow.destroy()
                    label._tipwindow = None
            label.bind("<Enter>", show_tip)
            label.bind("<Leave>", hide_tip)

        ultimo_csv = cargar_ultimo_csv(tipo_archivo)
        if ultimo_csv and os.path.exists(ultimo_csv):
            variable.set(ultimo_csv)

        def seleccionar_archivo():
            ruta = seleccionar_y_guardar_csv(tipo_archivo)
            if ruta:
                variable.set(ruta)

        entry = tk.Entry(frame, textvariable=variable, width=50, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        entry.pack(pady=5)
        entry.config(relief="groove", bd=2)

        marco_botones = tk.Frame(frame, bg="#e8f4f8")
        marco_botones.pack(pady=3)

        crear_boton(marco_botones, texto="Seleccionar Archivo", comando=seleccionar_archivo, bg="#b6d7a8", fg="#222222", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        crear_boton(marco_botones, texto="Editar Archivo", comando=comando_editar, bg="#9fc5e8", fg="#222222", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
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
        label = tk.Label(frame, text=titulo, bg="#e8f4f8", fg="#1a5276", font=("Segoe UI", 11, "bold"))
        label.pack(pady=3)
        if tooltip_text:
            def show_tip(event):
                tip = tk.Toplevel()
                tip.wm_overrideredirect(True)
                tip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
                tk.Label(tip, text=tooltip_text, bg="#fafdff", fg="#333333", relief="solid", borderwidth=1, font=("Segoe UI", 9)).pack()
                label.tipwindow = tip
            def hide_tip(event):
                if hasattr(label, 'tipwindow'):
                    label.tipwindow.destroy()
            label.bind("<Enter>", show_tip)
            label.bind("<Leave>", hide_tip)

    # Horas de trabajo
    marco_labor = tk.Frame(marco_combinado, bg="#e8f4f8")
    marco_labor.pack(side="left", padx=10)
    tk.Label(marco_labor, text="Horas de trabajo:", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    entrada_labor = tk.Entry(marco_labor, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    entrada_labor.insert(0, "1.5")
    entrada_labor.pack()

    # Porcentaje de ganancia
        entry = tk.Entry(frame, textvariable=variable, width=50, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        entry.pack(pady=5)
        entry.config(relief="groove", bd=2)
    marco_ganancia.pack(side="left", padx=10)
    tk.Label(marco_ganancia, text="Porcentaje de ganancia (%):", bg="#e8f4f8", fg="#333333", font=("Arial", 9)).pack()
    entrada_ganancia = tk.Entry(marco_ganancia, bg="#ffffff", fg="#333333", font=("Arial", 9), width=10, justify="center")
    entrada_ganancia.insert(0, "35")
        crear_boton(marco_botones, texto="Seleccionar Archivo", comando=seleccionar_archivo, bg="#b6d7a8", fg="#222222", font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)
        if tooltip_text is not None:
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

