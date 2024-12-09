import pandas as pd
import numpy as np
from tqdm import tqdm
from utils import *
import time
import json
import sys
import re
from concurrent.futures import ThreadPoolExecutor


def analyze_promo_v2_wrapper(row):
    try:
        return analyze_promo_v2(image_path=row)
    except Exception as e:
        print(f"Error processing {row}: {e}")
        return {'error': str(e), 'image_path': row}


def parallel_process(df, func, workers=4):
    """
    Paraleliza la ejecución de una función sobre un DataFrame usando threads
    """
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(func, df['url_img']))
    return results


def main(argv):
    assert argv[1] in ['falabella', 'paris', 'lider-supermercado', 'lider-catalogo', 'jumbo'],\
        'retails supported: falabella, paris, lider-supermercado, lider-catalogo, jumbo as argv'

    try:
        # import df
        df = pd.read_csv(f'./data_retails/promos_home/df_promos_retail_{argv[1]}.csv', index_col=0)
        print(df)
        print('analyzing...')
        start = time.time()
        # analyze imgs with ai assistant
        df['promo_analysis'] = parallel_process(df, analyze_promo_v2_wrapper, workers=8)
        df['descripcion_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='promocion'))
        df['duracion_promo'] = df['promo_analysis'].apply(lambda row: get_promo_data(row, key='duracion_promo'))
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
        # save as csv
        df.to_csv(f'./data_retails/promos_home_analysis/df_promos_retail_analysis_{argv[1]}.csv')
        total = round(time.time() - start,2)
        print(f'time taken: {total} secs')

    except Exception as e:
        print(f"Error al procesar las promociones")
        return {'error': str(e)}


if __name__ == '__main__':
    main(sys.argv)
