import os
import csv
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import state

def calculate_with_ai(csv_file, recipe_input, packaging_csv, packaging_materials, fixed_costs, labor_hours, profit_margin, response_text):
    global hidden_parts_global  # Usar la variable global

    try:
        if not os.path.exists(csv_file):
            raise FileNotFoundError("CSV file not found.")

        # Load CSVs
        with open(csv_file, mode='r', encoding='utf-8') as file:
            contenido_csv_ingredientes = [row for row in csv.reader(file)]
        with open(packaging_csv, mode='r', encoding='utf-8') as archivo:
            contenido_csv_packaging = [row for row in csv.reader(archivo)]

        labor_cost = float(labor_hours) * 250

        prompt = f"""
        Teniendo en cuenta la información de los archivos CSV proporcionados, donde el primero tiene ingredientes y sus costos correspondientes, ({contenido_csv_ingredientes}), calcula el costo del postre teniendo en cuenta los siguientes ingredientes: {recipe_input}.
        El segundo CSV tiene los materiales y sus costos correspondientes, ({contenido_csv_packaging}), calcula el costo del packaging teniendo en cuenta los siguientes materiales: {packaging_materials}.
        Ten en cuenta el valor total del packaging, ${fixed_costs} por los gastos fijos, ${labor_cost} por horas de trabajo (h).
        Calcula el total de gastos que es ingredientes + packaging + gastos fijos, la ganancia si se desea que sea un {profit_margin}% del total de gastos (sin tener en cuenta horas de trabajo), la ganancia en mano que es ganancia + mano de obra y el valor final.
        No me respondas el paso a paso ni el código ni el proceso.
        Respondeme los siguientes puntos:
        1. Cálculo de ingredientes (Los cálculos que hiciste para encontrar el valor de cada ingrediente en el siguiente formato:)
        ingrediente: cantidad (con la conversión si es necesario a la medida del CSV) * costo = $ resultado

        2. Cálculo de packaging (Los cálculos que hiciste para encontrar el valor de cada material en el siguiente formato:)
        material: cantidad (normalizada) * costo = $ resultado

        3. Cálculo final (Los demás cálculos)
            Ingredientes: $ resultado
            Packaging: $ resultado
            Gastos fijos: $ resultado
            Total de gastos: $ resultado

            Valor de horas de trabajo: $ resultado
            Ganancia: $ resultado
            Ganancia total (en mano): $ resultado
            
            ---------------------------
            Precio final: $ resultado
            ---------------------------

        4. Lista de ingredientes consumidos (Escritos igual que en el CSV y con las cantidades convertidas a las medidas del CSV sin mencionar la medida, en el siguiente formato, separados por líneas:)
            ingrediente: cantidad

        5. Lista de materiales consumidos (Escritos igual que en el CSV y en las medidas del CSV sin mencionarlas, en el siguiente formato, separados por líneas:)
            material: cantidad
        """

        # Load environment variables. Dynamically determine the path of the .env file
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        env_path = os.path.join(base_path, ".env")
        load_dotenv(dotenv_path=env_path)

        # Configure the Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GENAI_API_KEY"),
            temperature=0
        )
        response = llm.invoke(input=prompt).content
        visible_part, hidden_part = split_response_parts(response)

        # Guardar las partes ocultas en la variable global
        state.hidden_parts_global = hidden_part

        # Mostrar solo las partes visibles en la interfaz
        response_text.set(visible_part)

    except Exception as e:
        return f"Error: {e}"


def consume_stock_logic(hidden_part, ingredients_csv_path, packaging_csv_path):
    try:
        # Extraer las listas de consumo de ingredientes y materiales
        ingredients_usage = extract_usage_list(hidden_part, section="Lista de ingredientes consumidos")
        packaging_usage = extract_usage_list(hidden_part, section="Lista de materiales consumidos")

        # Actualizar los CSVs con las cantidades utilizadas
        update_csv_stock(ingredients_csv_path, ingredients_usage)
        update_csv_stock(packaging_csv_path, packaging_usage)
    except Exception as e:
        raise Exception(f"Error al procesar el stock: {e}")

def extract_usage_list(response_text, section):
    """Extrae las cantidades usadas de una lista en el texto de resultados."""
    usage = {}
    try:
        start_section = f"{section}"
        end_section = "\n\n"  # Asume que hay dos saltos de línea entre secciones
        section_text = response_text.split(start_section)[1].split(end_section)[0]
        for line in section_text.strip().split("\n"):
            name, quantity = line.split(": ")
            usage[name.strip()] = float(quantity.strip())
    except Exception:
        raise Exception(f"No se pudo procesar la sección {section}.")
    return usage


def update_csv_stock(csv_path, usage_data):
    """Actualiza el stock en un CSV dado según los datos de uso."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo CSV no encontrado: {csv_path}")

    updated_rows = []
    try:
        # Leer el archivo existente
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)
            if "Stock" not in headers:
                raise KeyError("El CSV no contiene una columna 'Stock'.")

            stock_index = headers.index("Stock")
            name_index = headers.index(headers[0])  # Primera columna (Ingrediente o Material)

            # Mantener encabezados
            updated_rows.append(headers)

            # Actualizar filas
            for row in reader:
                name = row[name_index]
                if name in usage_data:
                    current_stock = float(row[stock_index])
                    required_quantity = usage_data[name]
                    
                    # Verificar si hay suficiente stock
                    if current_stock < required_quantity:
                        raise ValueError(f"Stock insuficiente para '{name}': disponible={current_stock}, requerido={required_quantity}")
                    
                    # Actualizar stock
                    row[stock_index] = str(current_stock - required_quantity)
                updated_rows.append(row)

        # Escribir los datos actualizados de vuelta al archivo
        with open(csv_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)

    except Exception as e:
        raise Exception(f"Error al actualizar el archivo CSV {csv_path}: {e}")

def split_response_parts(response_text):
    """Divide la respuesta en partes visibles y ocultas."""
    try:
        # Encuentra las partes visibles (1-3) y ocultas (4-5)
        visible_end = response_text.find("4. Lista de ingredientes")
        visible_part = response_text[:visible_end].strip()
        hidden_start = response_text.find("4. Lista de ingredientes")
        hidden_part = response_text[hidden_start:].strip()
        return visible_part, hidden_part
    except Exception:
        raise Exception("Error al dividir las partes visibles y ocultas del texto de respuesta.")
