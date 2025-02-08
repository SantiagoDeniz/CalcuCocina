import os, csv, sys
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
        C (Contexto)
        Se dispone de dos archivos CSV con información de costos y medidas:

        Archivo de ingredientes ({contenido_csv_ingredientes}), que contiene una lista de ingredientes con sus costos y las unidades de medida correspondientes.
        Archivo de materiales de empaque ({contenido_csv_packaging}), que contiene una lista de materiales de packaging con sus respectivos costos y medidas.
        El objetivo es calcular el costo total de producir un postre a partir de ciertos ingredientes ({recipe_input}) y de empaquetarlo con determinados materiales ({packaging_materials}). Es imprescindible convertir las unidades de medida en caso de que las proporciones solicitadas difieran de las indicadas en el CSV (por ejemplo, no confundir gramos con kilogramos, ni litros con mililitros).

        Una vez obtenidos los costos de ingredientes y packaging, se deben considerar además los gastos fijos (${fixed_costs}), el costo por horas de trabajo (${labor_cost}) y el margen de ganancia deseado ({profit_margin}%) para calcular:

        El costo total de producción (ingredientes + packaging + gastos fijos).
        La ganancia si se desea que sea un porcentaje del total de gastos (sin incluir el valor de la mano de obra en la base de cálculo).
        El total “en mano”, que integra la ganancia y las horas de trabajo.
        El precio final.
        R (Rol)
        Actúa como un experto líder en la industria de la pastelería y la gestión de costos, con más de dos décadas de experiencia en el cálculo de costos, optimización de recetas y análisis de rentabilidad. Eres reconocido internacionalmente por tu habilidad para integrar la rentabilidad y la precisión financiera en el desarrollo de productos alimenticios.

        A (Acción)

        Lee la información del CSV de ingredientes y del CSV de materiales de empaque.
        Aplica las conversiones de unidades necesarias para que los datos de la receta ({recipe_input}) y los materiales ({packaging_materials}) coincidan con la unidad de medida del CSV correspondiente.
        Calcula el costo total de los ingredientes, detallando para cada uno: la cantidad exacta utilizada (ya convertida), el costo unitario y el costo resultante.
        Calcula el costo total del packaging, detallando para cada material: la cantidad exacta utilizada (ya convertida) y su costo.
        Suma los gastos fijos (${fixed_costs}) a los costos de ingredientes y packaging para obtener el costo total de gastos.
        Aplica el margen de ganancia deseado ({profit_margin}%) al total de gastos, sin incluir el costo de la mano de obra en el cálculo de esta ganancia, y súmale la mano de obra (${labor_cost}) para obtener la “ganancia total en mano”.
        Muestra el precio final, que es la suma de los gastos totales y la ganancia total en mano.
        No detalles el paso a paso ni muestres código o proceso; únicamente reporta los resultados en el formato que se describe a continuación, respetando el número de saltos de línea solicitados.
        F (Formato)
        El resultado se presentará en un bloque de texto con la siguiente estructura (con el número exacto de saltos de línea indicado y sin añadir explicaciones extra):

            1. Cálculo de ingredientes (uno por línea):
            ingrediente: cantidad_conversión * costo = $resultado [aclaración de la conversión si se realizó]
            ... (repetir para cada ingrediente) ...

            2. Cálculo de packaging (uno por línea):
            material: cantidad_conversión * costo = $resultado
            ... (repetir para cada material) ...

            3. Cálculo final
                Ingredientes: $resultado
                Packaging: $resultado
                Gastos fijos: $resultado
                Total de gastos: $resultado

                Valor de horas de trabajo: $resultado
                Ganancia: $resultado
                Ganancia total (en mano): $resultado
                
                ---------------------------
                Precio final: $resultado
                ---------------------------

            === NO INCLUIR ESTO EN EL MENSAJE PRINCIPAL ===

            4. Lista de ingredientes consumidos (uno por línea, cantidades en la unidad del CSV sin mencionar la unidad):
            ingrediente: cantidad
            ingrediente: cantidad

            5. Lista de materiales consumidos (uno por línea, cantidades en la unidad del CSV sin mencionar la unidad):
            material: cantidad
            material: cantidad

        Nota:

        No proporcionar ningún paso de cálculo o explicación adicional.
        No incluir información distinta a la solicitada.
        Respetar estrictamente el orden, el contenido y los saltos de línea solicitados.
        Incluir todas las aclaraciones de conversión solo entre corchetes al final de cada cálculo de ingrediente, si es necesario.
        T (Público objetivo)
        Esta instrucción está dirigida específicamente a Gemini, con el fin de que genere la respuesta final de acuerdo con los cálculos de costos, conversiones de unidades y ganancias requeridas. En última instancia también está  dirigida a los usuarios que soliciten la consulta, usualmente cocineros o pasteleros emprendedores.
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
        print(response)
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
        ingredients_usage = extract_usage_list(hidden_part, section="Lista de ingredientes consumidos:")
        packaging_usage = extract_usage_list(hidden_part, section="Lista de materiales consumidos:")

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
        raise Exception(f"No se pudo procesar la sección '{section}'.")
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
    try:
        visible_end = response_text.find("=== NO INCLUIR ESTO EN EL MENSAJE PRINCIPAL ===")
        
        if visible_end == -1:
            raise ValueError("No se encontró el delimitador en la respuesta.")

        visible_part = response_text[:visible_end].strip()
        hidden_part = response_text[visible_end:].strip()

        return visible_part, hidden_part
    except Exception:
        raise Exception("Error al dividir las partes visibles y ocultas del texto de respuesta.")

