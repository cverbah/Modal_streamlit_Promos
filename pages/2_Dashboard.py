import pandas as pd
import numpy as np
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import os
import streamlit as st
from datetime import datetime, timedelta
from streamlit_extras.app_logo import add_logo
from utils_plots import plot_wordcloud, plot_against_offer_type, plot_col_against_date
from streamlit_carousel import carousel

st.set_page_config(
    page_title="Dashboard Testing",
    page_icon="	:gear:",
    layout="wide",
)
#add_logo("https://www.python.org/static/community_logos/python-powered-w-100x40.png", height=1)
st.title('Dashboard Promociones')
try:
    with st.spinner('Cargando datos...'):
        df = st.session_state.df
        df_filtered = pd.DataFrame()
        #st.dataframe(df)


except Exception as e:
    st.error('No se ha cargado archivo con promociones')

if 'tipo_oferta' in df.columns.tolist():
    with st.sidebar:
        st.title(':gear: Filtros')
        # offer filters
        offer_type = df['tipo_oferta'].unique().tolist()
        offer_type.extend(['todas'])
        select_offer = st.selectbox('Seleccione el tipo de oferta', offer_type, index=len(offer_type) - 1)

        # column filter
        col_types = ['categorias_en_promo', 'marcas_en_promo', 'publico_objetivo']
        df_col = st.selectbox('Seleccione columna', col_types, index=len(col_types) - 1)

        # dataframe filter
        if select_offer:

            if select_offer != 'todas':
                df_filtered = df[(df.tipo_oferta == select_offer)].reset_index(drop=True)
            else:
                df_filtered = df.reset_index(drop=True)
            df_filtered.drop(columns=['datetime_checked'], inplace=True)

    try:
        col1, col2 = st.columns((0.8, 0.2), gap='small')
        if len(df_filtered) > 0:
            st.subheader("DataFrame Filtrado:")
            st.dataframe(df_filtered)

            with col2:
                pass

            rows = st.columns(2)
            grid = [col.container(height=500) for col in rows]
            with grid[0]:
                with st.spinner('Cargando gráficos...'):
                    st.markdown(f"<h1 style='text-align: left;font-size: 17px;'>WordCloud</h1>", unsafe_allow_html=True)
                    fig = plot_wordcloud(df_filtered, df_col, color='white', max_words=20)
                    st.pyplot(fig)
            with grid[1]:

                with st.spinner('Cargando gráficos...'):
                    fig = plot_against_offer_type(df_filtered, df_col, top=5, height=450, width=600)
                    st.plotly_chart(fig, theme="streamlit")

            #with col4:
            #    pass
    except Exception as e:
        st.error(e)
else:
    st.write(':gear: Dashboard solo disponible para test de promociones por ahora :gear:')


