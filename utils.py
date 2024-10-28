import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from PIL import Image
import json
import vertexai
import matplotlib.pyplot as plt
import io
import contextlib
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import time

# env
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key.json'
GOOGLE_API_KEY = os.environ['GCP_API_KEY']
PROJECT_ID = 'automatch-309218'
LOCATION = "us-central1"
GCP_MODEL_ID = "gemini-1.5-flash-002"
vertexai.init(project=PROJECT_ID, location=LOCATION)
gcp_model = ChatGoogleGenerativeAI(temperature=0, model=GCP_MODEL_ID, google_api_key=GOOGLE_API_KEY)


def get_promo_data(row, key):
    assert key in ['index', 'categorias_en_promo', 'marcas_en_promo', 'cuotas_sin_interes', 'cupon_app', 'promociones_envio',
                   'publico_objetivo', 'promocion', 'productos_en_oferta', 'duracion_promo'], 'wrong key'

    if row == 'img loading problem':
        return np.nan

    row_dict = row[0]
    if row_dict != '':
        try:
            return row_dict[key]
        except:
            return np.nan

    if row_dict == np.nan or row_dict == None:
        return np.nan


def extract_discount(string):
    pattern = r'\b\d+(?:\.\d+)?%'
    discounts = re.findall(pattern, string)
    if discounts:

        discounts_float = list(map(lambda d: float(d.strip('%')) / 100, discounts))
        return discounts_float[0] #por ahora entrega el primero que encuentra
    else:
        return np.nan


def format_as_percentage(value):
    if pd.isnull(value):
        return np.nan
    else:
        return f"{value:.0%}"


def analyze_data(df: pd.DataFrame):
    #df['promo_analysis'] = df['url_img'].apply(lambda row: analyze_promo_v2(row))
    # json to cols
    df['descripcion_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='promocion'))  #ok
    df['duracion_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='duracion_promo')) #ok
    df['descuentos_promo'] = df['descripcion_promo'].apply(lambda row: extract_discount(str(row)))
    df['descuentos_promo'] = df['descuentos_promo'].apply(lambda row: format_as_percentage(row))
    df['categorias_en_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='categorias_en_promo'))
    df['marcas_en_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='marcas_en_promo'))
    df['publico_objetivo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='publico_objetivo'))
    df['productos_en_oferta'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='productos_en_oferta'))
    df['cuotas_sin_interes'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='cuotas_sin_interes'))
    df['cupon_app'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='cupon_app'))
    df['promociones_envio'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='promociones_envio'))
    df.drop(columns='promo_analysis', inplace=True)


def analyze_promo_v2(image_path, format=True, model=gcp_model):
    '''' just testing for now : same example from gcp'''

    instructions = "Instrucciones: Las siguientes imágenes contienen promociones de retails, extrae información de las promociones.Solo usa la información" \
                   "disponible en las imágenes. Siempre respondes en español y en minúsculas."
    prompt = """
    Extrae la información siguiendo estos pasos y guardando la información en un archivo json siguiendo la siguiente estructura:
    [{'index': indice de imágen partiendo con 1}]
    Paso 1: Analiza las ofertas y promociones de manera general presentes en cada imágen, respondiendo las siguientes preguntas,
    agregando los datos al archivo json:\
    'categorias_en_promo': Sobre qué categorías trata la promoción? Usa siempre 3 palabaras claves y almacénalas en una lista.  
    'marcas_en_promo': Qué marcas están con promoción? Almacena todas las marcas detectadas en una lista. Si no hay, devuelve null.
    'duracion_promo': [{'fecha_inicio_promo': fecha inicio promoción con el siguiente formato de fecha: dd/mm/aaaa,
                        'fecha_termino_promo: fecha termino promoción con el siguiente formato de fecha: dd/mm/aaaa,
                        'dias_duracion': días que dura la promoción con formato: int}]. Si no hay fechas, devuelve null.
    'cuotas_sin_interes': Es posible comprar en cuotas sin interés? Si es que sí, cuantas cuotas? en formato: int. Si no detectas la palabra cuota, devuelve null.
    'cupon_app': Hay cupones de descuento usando sólo la app del retail? Si es que hay, extrae la información. Si no hay, devuelve null.
    'promociones_envio': Hay promociones para el envío?  Si es que hay, describe la promoción. Si no hay, devuelve null.
    'publico_objetivo': Cual crees que es el público objetivo de esta promoción?
                        Devuelve 5 adjetivos calificativos del público objetivo  y almacénalas en una lista. Usa 1 palabra para representar cada característica.
    [{'promocion': analisis del paso 1 y de la promoción principal de la imágen. Nunca inventes datos si no aparecen en la imágen.}]
    Paso 2: Identifica cuantos productos con precios con descuentos hay en la imagen, mostrando el precio sin y con descuento.
            Si no sale el precio de cada producto de forma explícita, no guardes la información.
    Paso 3: Extra la información de cada producto siempre y cuando tenga descuentos y agregala al archivo json siguiendo la siguiente estructura:\
    ['productos_en_oferta': [{'nombre_del_producto': nombre completo del producto detectado,
                              'precio_normal': precio normal,
                              'precio_oferta': precio oferta,
                              'descuento': descuento formateado con porcentaje]}]
    Si no logras detectar productos específicos con precios con descuento en la imagen, devuelve la lista vacía.
    Considera siempre todos los 0 en los precios de los productos.
    Paso 4: Si no es posible extraer ciertos datos de la imagen, guardar el dato como null
    Paso 5: Formatea el archivo. Elimina caractéres especiales si es necesario.
    """
    try:
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"{instructions}",
                },
                {"type": "image_url",
                 "image_url": image_path},
                {"type": "text",
                 "text": prompt},
            ]
        )
        response = model.invoke([message]).content

        if format:
            response = response.replace('```json', '').replace('\n```', '')
            response = json.loads(response)

        return response

    except Exception as e:
        print(e)
        return 'img loading problem'


def parse_null_list(value):
    if pd.isnull(value):
        parse = '[]'
        return parse
    else:
        return value


def execute_code(snippet, df: pd.DataFrame):
    # Strip the code snippet
    code = snippet.strip().strip('```python').strip('```').strip()
    local_vars = {'df': df, 'plt': plt}
    # Redirect standard output to capture `print()` statements
    output_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(output_capture):
            exec(code, globals(), local_vars)
        output = output_capture.getvalue()
        return local_vars, output
    except Exception as e:
        return {}, f"Error: {e}"


def format_pricing_table(df):
    df = df.iloc[:, :9]
    df.columns = (df.columns.
                  str.replace(' ', '_').
                  str.lower().
                  str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

    df['sku'] = df['sku'].astype(str)
    df['mas_bajo'] = df['mas_bajo'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    df['mas_alto'] = df['mas_alto'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    df['precio_mercado'] = df['precio_mercado'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    df['precio_de_lista'] = df['precio_de_lista'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    df = df.reset_index(drop=True)
    return df


def format_compete_table(df):
    df.columns = (df.columns.
                  str.replace(' ', '_').
                  str.lower().
                  str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

    df['sku_tienda'] = df['sku_tienda'].astype(str)
    df['fecha'] = pd.to_datetime(df['fecha'])
    #df['precio_normal'] = df['precio_normal'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    #df['precio_final'] = df['precio_final'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))
    #df['precio_tarjeta'] = df['precio_tarjeta'].apply(lambda row: int(row.replace('$ ', '').replace(',', '')))

    df = df.reset_index(drop=True)
    return df
