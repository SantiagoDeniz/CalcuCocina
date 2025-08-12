# gui.py

import tkinter as tk
from tkinter import messagebox, PhotoImage
import os
import sys
from logic import calcular_con_ia, consumir_stock_logica
from utils import cargar_ultimo_csv, guardar_ultimo_csv, seleccionar_y_guardar_csv
from editor import editar_csv_ingredientes, editar_csv_packaging
import state

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def crear_boton(padre, texto, comando, bg="#f4cccc", fg="#333333", font=("Arial", 9), **kwargs):
    btn = tk.Button(padre, text=texto, command=comando, bg=bg, fg=fg, font=font,
                    activebackground="#b6d7a8", activeforeground="#222222", cursor="hand2", **kwargs)
    def on_enter(e):
        btn['bg'] = '#b6d7a8'
    def on_leave(e):
        btn['bg'] = bg
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def crear_cargador_csv(marco_padre, titulo, variable, tipo_archivo, comando_editar, tooltip_text=None):
    frame = tk.Frame(marco_padre, bg="#e8f4f8")
    frame.pack(fill="x", pady=5)
    label = tk.Label(frame, text=titulo, bg="#e8f4f8", fg="#1a5276", font=("Arial", 11, "bold"))
    label.pack(pady=3)
    tipwindow = None
    if tooltip_text:
        def show_tip(event):
            nonlocal tipwindow
            tipwindow = tk.Toplevel()
            tipwindow.wm_overrideredirect(True)
            tipwindow.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            tk.Label(tipwindow, text=tooltip_text, bg="#fafdff", fg="#333333", relief="solid", borderwidth=1, font=("Segoe UI", 9)).pack()
        def hide_tip(event):
            nonlocal tipwindow
            if tipwindow is not None:
                tipwindow.destroy()
                tipwindow = None
        label.bind("<Enter>", show_tip)
        label.bind("<Leave>", hide_tip)
    ultimo_csv = cargar_ultimo_csv(tipo_archivo)
    if ultimo_csv and os.path.exists(ultimo_csv):
        variable.set(ultimo_csv)
    def seleccionar_archivo():
        ruta = seleccionar_y_guardar_csv(tipo_archivo)
        if ruta:
            variable.set(ruta)
    entry = tk.Entry(frame, textvariable=variable, width=50, bg="#ffffff", fg="#333333", font=("Arial", 10))
    entry.pack(pady=5)
    entry.config(relief="groove", bd=2)
    marco_botones = tk.Frame(frame, bg="#e8f4f8")
    marco_botones.pack(pady=3)
    crear_boton(marco_botones, texto="Seleccionar Archivo", comando=seleccionar_archivo, bg="#b6d7a8", fg="#222222", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    crear_boton(
        marco_botones,
        texto="Editar Archivo",
        comando=lambda: comando_editar(variable.get()),
        bg="#9fc5e8",
        fg="#222222",
        font=("Arial", 10, "bold")
    ).pack(side="left", padx=5)

def crear_ventana_principal(raiz):
    raiz.configure(bg="#cce7e8")
    raiz.option_add("*Font", "Arial 10")
    raiz.minsize(950, 650)

    # Área de ayuda rápida (arriba de todo)
    ayuda_frame = tk.Frame(raiz, bg="#e3f0fa", bd=2, relief="groove")
    ayuda_frame.pack(side="top", fill="x", padx=10, pady=7)

    ayuda_frame.columnconfigure(0, weight=1)
    ayuda_frame.columnconfigure(1, weight=0)

    # Título centrado
    label_titulo = tk.Label(ayuda_frame, text="Bienvenido a CalcuCocina", bg="#e3f0fa", fg="#1a5276", font=("Arial", 15, "bold"))
    label_titulo.grid(row=0, column=0, sticky="ew", padx=10, pady=2)

    # Botón de ayuda tipo lamparita
    icono_lampara = None
    try:
        icono_path = os.path.join("assets", "icono.ico")
        icono_lampara = tk.PhotoImage(file=icono_path)
    except Exception:
        icono_lampara = None

    btn_ayuda = tk.Label(ayuda_frame, bg="#e3f0fa", cursor="question_arrow")
    if icono_lampara:
        btn_ayuda.config(image=icono_lampara)
        btn_ayuda.image = icono_lampara
    else:
        btn_ayuda.config(text="💡", font=("Arial", 16))
    btn_ayuda.grid(row=0, column=1, sticky="e", padx=10)

    # Tooltip instructivo
    instructivo = (
        "1. Sube tus archivos CSV de ingredientes y packaging.\n"
        "2. Escribe tu receta y materiales.\n"
        "3. Completa gastos, horas y ganancia.\n"
        "4. Haz clic en 'Calcular con IA'.\n"
        "5. Usa 'Consumir Stock' para actualizar el inventario."
    )
    tipwindow = None
    def show_tip(event):
        nonlocal tipwindow
        if tipwindow is not None:
            return
        tipwindow = tk.Toplevel(ayuda_frame)
        tipwindow.wm_overrideredirect(True)
        # Mostrar el pop-up hacia abajo a la izquierda del botón
        x = btn_ayuda.winfo_rootx() - tipwindow.winfo_reqwidth() - 100
        y = btn_ayuda.winfo_rooty() + btn_ayuda.winfo_height() + 5
        # Si x es negativo, lo dejamos en 0 para que no se salga de la pantalla
        if x < 0:
            x = 0
        tipwindow.geometry(f"+{x}+{y}")
        tk.Label(tipwindow, text=instructivo, bg="#fafdff", fg="#333333", relief="solid", borderwidth=1, font=("Arial", 10), justify="left", anchor="w").pack(ipadx=8, ipady=6)
    def hide_tip(event):
        nonlocal tipwindow
        if tipwindow is not None:
            tipwindow.destroy()
            tipwindow = None
    btn_ayuda.bind("<Enter>", show_tip)
    btn_ayuda.bind("<Leave>", hide_tip)

    # Frame principal con dos columnas
    frame_principal = tk.Frame(raiz, bg="#cce7e8")
    frame_principal.pack(fill="both", expand=True)

    marco_izquierdo = tk.Frame(frame_principal, bg="#e8f4f8")
    marco_izquierdo.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    marco_derecho = tk.Frame(frame_principal, bg="#e8f4f8")
    marco_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Variables para rutas de archivos
    ruta_csv_ingredientes = tk.StringVar()
    ruta_csv_packaging = tk.StringVar()

    # Cargadores de CSV
    crear_cargador_csv(
        marco_izquierdo,
        "Archivo de Ingredientes:",
        ruta_csv_ingredientes,
        "ingredients",
        editar_csv_ingredientes,
        tooltip_text="Selecciona o edita el archivo CSV de ingredientes."
    )
    crear_cargador_csv(
        marco_izquierdo,
        "Archivo de Packaging:",
        ruta_csv_packaging,
        "packaging",
        editar_csv_packaging,
        tooltip_text="Selecciona o edita el archivo CSV de materiales de packaging."
    )

    tk.Frame(marco_izquierdo, bg="#cce7e8", height=5).pack(fill="x", pady=2)

    # Entradas de receta y packaging
    tk.Label(marco_izquierdo, text="Receta (ingredientes y cantidades):", bg="#e8f4f8", fg="#333333", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    texto_receta = tk.Text(marco_izquierdo, height=7, width=60, bg="#ffffff", fg="#333333", font=("Arial", 9))
    texto_receta.pack(pady=3)
    tk.Label(marco_izquierdo, text="Materiales de Packaging (y cantidades):", bg="#e8f4f8", fg="#333333", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    texto_packaging = tk.Text(marco_izquierdo, height=4, width=60, bg="#ffffff", fg="#333333", font=("Arial", 9))
    texto_packaging.pack(pady=3)

    # Frame para gastos fijos, horas de trabajo y ganancia
    marco_otros = tk.Frame(marco_izquierdo, bg="#e8f4f8")
    marco_otros.pack(fill="x", pady=10)
    marco_gastos_labor_ganancia = tk.Frame(marco_otros, bg="#e8f4f8")
    marco_gastos_labor_ganancia.pack()
    marco_combinado = tk.Frame(marco_gastos_labor_ganancia, bg="#e8f4f8")
    marco_combinado.pack(anchor="center", pady=5)

    # Botón Calcular con IA (al final de la columna izquierda)
    def comando_calcular():
        if not validar_entradas_numericas():
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos en gastos, horas y ganancia.")
            return
        calcular_con_ia(
            ruta_csv_ingredientes.get(),
            texto_receta.get("1.0", tk.END).strip(),
            ruta_csv_packaging.get(),
            texto_packaging.get("1.0", tk.END).strip(),
            entrada_gastos.get().strip(),
            entrada_labor.get().strip(),
            entrada_ganancia.get().strip(),
            texto_resultado
        )
    crear_boton(
        marco_izquierdo,
        texto="Calcular con IA",
        comando=comando_calcular,
        bg="#4caf80",
        fg="#ffffff",
        font=("Arial", 12, "bold")
    ).pack(pady=10)

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


    # Logo al inicio de la columna derecha
    try:
        if hasattr(sys, '_MEIPASS'):
            ruta_logo = os.path.join(getattr(sys, '_MEIPASS'), "assets/logo.png")
        else:
            ruta_logo = "assets/logo.png"
        logo_img = PhotoImage(file=ruta_logo).subsample(6, 6)
        etiqueta_logo = tk.Label(marco_derecho, image=logo_img, bg="#e8f4f8")
        etiqueta_logo.image = logo_img  # Referencia estándar para evitar garbage collection
        etiqueta_logo.pack(pady=7)
    except Exception as e:
        tk.Label(marco_derecho, text=f"[Logo no encontrado: {e}]", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=10)

    # Resultado
    tk.Label(marco_derecho, text="Resultado:", bg="#e8f4f8", fg="#333333", font=("Arial", 10)).pack(pady=3)
    texto_resultado = tk.StringVar()
    display_resultado = tk.Text(marco_derecho, height=25, width=50, wrap="word", bg="#ffffff", fg="#333333", font=("Arial", 9))
    display_resultado.pack(pady=2, padx=5)

    def actualizar_resultado(*args):
        display_resultado.delete("1.0", tk.END)
        display_resultado.insert(tk.END, texto_resultado.get())
    texto_resultado.trace_add("write", actualizar_resultado)

    # Botón Consumir Stock
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

    crear_boton(
        marco_derecho,
        texto="Consumir Stock",
        comando=consumir_stock,
        bg="#fff2f2",
        fg="#d32f2f",
        font=("Arial", 12, "bold")
    ).pack(pady=5)

def main():
    raiz = tk.Tk()
    raiz.title("CalcuCocina")
    crear_ventana_principal(raiz)
    raiz.mainloop()
