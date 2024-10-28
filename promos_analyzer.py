import pandas as pd
import numpy as np
from tqdm import tqdm
from utils import *
import time
import json
import sys
import re


def main(argv):
    assert argv[1] in ['falabella', 'paris', 'lider-supermercado', 'lider-catalogo', 'jumbo'],\
        'retails supported: falabella, paris, lider-supermercado, lider-catalogo, jumbo as argv'
    # import df
    df = pd.read_csv(f'./data_retails/promos_home/df_promos_retail_{argv[1]}.csv', index_col=0)
    print(df)
    print('analyzing...')
    start = time.time()
    df['promo_analysis'] = df['url_img'].apply(lambda row: analyze_promo_v2(row))
    # json to cols
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
    df.to_csv(f'./data_retails/promos_home_analysis/df_promos_retail_analysis_{argv[1]}.csv')
    total = round(time.time() - start,2)
    print(f'time taken: {total} secs')


if __name__ == '__main__':
    main(sys.argv)
