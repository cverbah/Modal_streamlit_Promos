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
    page_title="Analista Promociones",
    page_icon=":robot_face:",
    layout="wide",
)

st.title(':robot_face: Analista de  Promociones')

try:
    with st.spinner('Cargando datos...'):
        df = st.session_state.df

    if 'df_with_promo' not in st.session_state:
        st.session_state.df_with_promo = False

    if (len(st.session_state.df) > 0) & (st.session_state.df_with_promo == False):
        st.markdown("<span style='font-size: 20px;'>1 - Aprete el botón Analizar Ofertas para comenzar</span>",
                    unsafe_allow_html=True)

        if st.button('Analizar Ofertas'):
            with st.spinner('Analizando ofertas'):
                st.session_state.df['promo_analysis'] = st.session_state.df['url_img'].apply(lambda row:
                                                                                             analyze_promo_v2(row,
                                                                                                              format=True))
                analyze_data(st.session_state.df)
                st.subheader("DataFrame:")
                st.dataframe(st.session_state.df)
                st.session_state.df_with_promo = True

    elif st.session_state.df_with_promo:
        st.subheader("DataFrame con ofertas analizadas:")
        st.dataframe(st.session_state.df)

    else:
        st.warning('Tabla cargada no contiene datos. Intente de nuevo con otra tabla')

    if st.session_state.df_with_promo:
        st.subheader("Imágenes promociones:")
        promotions = df['nombre_promocion'].tolist()
        select_promotion = st.selectbox('Seleccione la promoción:', promotions, index=0)
        url_image = df[df['nombre_promocion'] == select_promotion].url_img.tolist()[0]

        st.image(url_image, caption=f"Promoción: {select_promotion}", use_column_width=True)


except Exception as e:
    st.error(e)
