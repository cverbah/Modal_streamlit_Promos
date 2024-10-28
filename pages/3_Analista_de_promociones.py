import streamlit as st
from utils import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
matplotlib.use('tkagg')
from PIL import Image
import os
import time


st.set_page_config(
    page_title="Images Analyst Testing 2",
    page_icon=":robot_face:",
    layout="wide",
)

st.title(':robot_face: Analista de  Promociones')

try:
    with st.spinner('Cargando datos...'):
        df = st.session_state.df

except Exception as e:
    st.error(e)

st.subheader("DataFrame:")
if len(df) > 0:
    st.dataframe(st.session_state.df.head())
    if st.button('Analizar Ofertas'):
        with st.spinner('Analizando ofertas'):
            st.session_state.df['promo_analysis'] = st.session_state.df['url_img'].apply(lambda row:
                                                                                         analyze_promo_v2(row,
                                                                                                          format=True))
            analyze_data(st.session_state.df)
            st.dataframe(st.session_state.df)

    col1, col2, col3 = st.columns(3, gap='large')
    with col1:
        st.header(':magic_wand: Análisis ofertas principales')
        try:
            df_op = df[df.tipo_oferta == 'ofertas_principales']
            #img_data = list(zip(df_op['url_img'], df_op['position'], df_op['name_img']))
            img_data = list(zip(df_op['posicion'], df_op['nombre_promocion'], df_op['categorias_en_promo'], df_op['publico_objetivo']))
            with st.spinner('Pensando...'):
                #response = analyze_promo_v4(img_data, promo_type='promociones principales', format=False, model=gcp_model_txt)
                st.write(response)
                st.success('Ok!')

        except Exception as e:
            st.error(e)

    with col2:
        st.header(':magic_wand: Análisis grid de ofertas')
        try:
            df_og = df[df.tipo_oferta == 'grid_ofertas']
            img_data = list(zip(df_og['posicion'], df_og['nombre_promocion'], df_og['categorias_en_promo'], df_og['publico_objetivo']))
            with st.spinner('Pensando...'):
                response = analyze_promo_v4(img_data, promo_type='promociones secundarias', format=False, model=gcp_model_txt)
                st.write(response)
                st.success('Ok!')

        except Exception as e:
            st.error(e)


    with col3:
        st.header(':magic_wand: Análisis de lo último')
        try:
            df_lu = df[df.tipo_oferta == 'lo_ultimo']
            img_data = list(zip(df_lu['url_img'], df_lu['posicion'], df_lu['nombre_promocion']))
            with st.spinner('Pensando...'):
                response = analyze_promo_v3(img_data, promo_type='lo más visto', format=True, model=gcp_model_vision)
                st.write(response)
                st.success('Ok!')

        except Exception as e:
            st.error(e)
