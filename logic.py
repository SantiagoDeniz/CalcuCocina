
import os
import csv
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import state

# --- Cambios y mejoras en español ---
def calcular_con_ia(
    archivo_csv: str,
    receta: str,
    archivo_packaging: str,
    materiales_packaging: str,
    gastos_fijos: str,
    horas_trabajo: str,
    margen_ganancia: str,
    texto_respuesta
) -> None:
    """
    Calcula el costo total usando IA y actualiza el texto de respuesta visible.
    """
    try:
        if not os.path.exists(archivo_csv):
            raise FileNotFoundError("No se encontró el archivo de ingredientes.")
        if not os.path.exists(archivo_packaging):
            raise FileNotFoundError("No se encontró el archivo de packaging.")

        # Cargar CSVs
        with open(archivo_csv, mode='r', encoding='utf-8') as f:
            contenido_ingredientes = [row for row in csv.reader(f)]
        with open(archivo_packaging, mode='r', encoding='utf-8') as f:
            contenido_packaging = [row for row in csv.reader(f)]

        try:
            costo_labor = float(horas_trabajo) * 250
        except Exception:
            raise ValueError("Las horas de trabajo deben ser un número válido.")

        prompt = f"""
        C (Contexto)
        Se dispone de dos archivos CSV con información de costos y medidas:

        Archivo de ingredientes ({contenido_ingredientes}), que contiene una lista de ingredientes con sus costos y las unidades de medida correspondientes.
        Archivo de materiales de empaque ({contenido_packaging}), que contiene una lista de materiales de packaging con sus respectivos costos y medidas.
        El objetivo es calcular el costo total de producir un postre a partir de ciertos ingredientes ({receta}) y de empaquetarlo con determinados materiales ({materiales_packaging}). Es imprescindible convertir las unidades de medida en caso de que las proporciones solicitadas difieran de las indicadas en el CSV (por ejemplo, no confundir gramos con kilogramos, ni litros con mililitros).

        Una vez obtenidos los costos de ingredientes y packaging, se deben considerar además los gastos fijos (${gastos_fijos}), el costo por horas de trabajo (${costo_labor}) y el margen de ganancia deseado ({margen_ganancia}%) para calcular:

        El costo total de producción (ingredientes + packaging + gastos fijos).
        La ganancia si se desea que sea un porcentaje del total de gastos (sin incluir el valor de la mano de obra en la base de cálculo).
        El total “en mano”, que integra la ganancia y las horas de trabajo.
        El precio final.
        R (Rol)
        Actúa como un experto líder en la industria de la pastelería y la gestión de costos, con más de dos décadas de experiencia en el cálculo de costos, optimización de recetas y análisis de rentabilidad. Eres reconocido internacionalmente por tu habilidad para integrar la rentabilidad y la precisión financiera en el desarrollo de productos alimenticios.

        A (Acción)

        Lee la información del CSV de ingredientes y del CSV de materiales de empaque.
        Aplica las conversiones de unidades necesarias para que los datos de la receta ({receta}) y los materiales ({materiales_packaging}) coincidan con la unidad de medida del CSV correspondiente.
        Calcula el costo total de los ingredientes, detallando para cada uno: la cantidad exacta utilizada (ya convertida), el costo unitario y el costo resultante.
        Calcula el costo total del packaging, detallando para cada material: la cantidad exacta utilizada (ya convertida) y su costo.
        Suma los gastos fijos (${gastos_fijos}) a los costos de ingredientes y packaging para obtener el costo total de gastos.
        Aplica el margen de ganancia deseado ({margen_ganancia}%) al total de gastos, sin incluir el costo de la mano de obra en el cálculo de esta ganancia, y súmale la mano de obra (${costo_labor}) para obtener la “ganancia total en mano”.
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

        # Cargar variables de entorno
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
        env_path = os.path.join(base_path, ".env")
        load_dotenv(dotenv_path=env_path)

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GENAI_API_KEY"),
            temperature=0
        )

        respuesta = llm.invoke(input=prompt).content
        print(respuesta)
        parte_visible, parte_oculta = dividir_partes_respuesta(respuesta)
        state.hidden_parts_global = parte_oculta
        texto_respuesta.set(parte_visible)
    except Exception as e:
        texto_respuesta.set(f"Error: {e}")



def consumir_stock_logica(parte_oculta: str, ruta_csv_ingredientes: str, ruta_csv_packaging: str) -> None:
    """
    Actualiza el stock de ingredientes y packaging según la parte oculta de la respuesta.
    """
    try:
        uso_ingredientes = extraer_lista_uso(parte_oculta, seccion="Lista de ingredientes consumidos:")
        uso_packaging = extraer_lista_uso(parte_oculta, seccion="Lista de materiales consumidos:")
        actualizar_stock_csv(ruta_csv_ingredientes, uso_ingredientes)
        actualizar_stock_csv(ruta_csv_packaging, uso_packaging)
    except Exception as e:
        raise Exception(f"Error al procesar el stock: {e}")


def extraer_lista_uso(texto_respuesta: str, seccion: str) -> dict:
    """
    Extrae las cantidades usadas de una lista en el texto de resultados.
    """
    uso = {}
    try:
        inicio = texto_respuesta.split(seccion)[1]
        fin = inicio.split("\n\n")[0]
        for linea in fin.strip().split("\n"):
            nombre, cantidad = linea.split(": ")
            uso[nombre.strip()] = float(cantidad.strip())
    except Exception:
        raise Exception(f"No se pudo procesar la sección '{seccion}'.")
    return uso




def actualizar_stock_csv(ruta_csv: str, datos_uso: dict) -> None:
    """
    Actualiza el stock en un CSV dado según los datos de uso.
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"Archivo CSV no encontrado: {ruta_csv}")
    filas_actualizadas = []
    try:
        with open(ruta_csv, mode="r", encoding="utf-8") as archivo:
            lector = csv.reader(archivo)
            encabezados = next(lector)
            if "Stock" not in encabezados:
                raise KeyError("El CSV no contiene una columna 'Stock'.")
            idx_stock = encabezados.index("Stock")
            idx_nombre = encabezados.index(encabezados[0])
            filas_actualizadas.append(encabezados)
            for fila in lector:
                nombre = fila[idx_nombre]
                if nombre in datos_uso:
                    stock_actual = float(fila[idx_stock])
                    cantidad_requerida = datos_uso[nombre]
                    if stock_actual < cantidad_requerida:
                        raise ValueError(f"Stock insuficiente para '{nombre}': disponible={stock_actual}, requerido={cantidad_requerida}")
                    fila[idx_stock] = str(stock_actual - cantidad_requerida)
                filas_actualizadas.append(fila)
        with open(ruta_csv, mode="w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerows(filas_actualizadas)
    except Exception as e:
        raise Exception(f"Error al actualizar el archivo CSV {ruta_csv}: {e}")


def dividir_partes_respuesta(texto_respuesta: str) -> tuple:
    try:
        fin_visible = texto_respuesta.find("=== NO INCLUIR ESTO EN EL MENSAJE PRINCIPAL ===")
        if fin_visible == -1:
            raise ValueError("No se encontró el delimitador en la respuesta.")
        parte_visible = texto_respuesta[:fin_visible].strip()
        parte_oculta = texto_respuesta[fin_visible:].strip()
        return parte_visible, parte_oculta
    except Exception:
        raise Exception("Error al dividir las partes visibles y ocultas del texto de respuesta.")

