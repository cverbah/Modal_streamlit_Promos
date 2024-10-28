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
st.title(':construction: Dashboard: :construction:')
try:
    with st.spinner('Cargando datos...'):
        df = st.session_state.df
        df_filtered = pd.DataFrame()


except Exception as e:
    st.error('No se ha cargado archivo con promociones')

if 'tipo_oferta' in df.columns.tolist():
    with st.sidebar:
        st.title(':gear: Filtros')
        # offer filters
        offer_type = df['tipo_oferta'].unique().tolist()
        offer_type.extend(['todas'])
        select_offer = st.selectbox('Seleccione el tipo de oferta', offer_type, index=len(offer_type) - 1)

        # date filters
        min_date = min(df['date_checked'])
        max_date = max(df['date_checked'])
        today = datetime.now()
        start = datetime.now() - timedelta(days=365)
        end = datetime.now() + timedelta(days=365)
        tab1 = st.tabs(["Filtro Funcionando"])
        with tab1:
            date_range = st.date_input("Seleccione el rango de fechas", (min_date, today), start, end, format="YYYY-MM-DD")

        # column filter
        col_types = ['categorias_en_promo', 'marcas_en_promo', 'publico_objetivo']
        df_col = st.selectbox('Seleccione columna', col_types, index=len(col_types) - 1)

        # dataframe filter
        if select_offer:
            if len(date_range) > 1:
                if select_offer != 'todas':
                    df_filtered = df[(df.tipo_oferta == select_offer) & (df.date_checked >= date_range[0]) & (df.date_checked <= date_range[1])].reset_index(drop=True)
                else:
                    df_filtered = df[(df.date_checked >= date_range[0]) & (df.date_checked <= date_range[1])].reset_index(drop=True)
                df_filtered.drop(columns=['datetime_checked'], inplace=True)

    try:
        col1, col2 = st.columns((0.8, 0.2), gap='small')
        if len(df_filtered) > 0:
            with col1:
                with st.spinner('Cargando datos...'):
                    items_carousel = [dict(title='', text=desc, img=img) for name, desc, img in
                                      list(zip(df_filtered['nombre_promocion'].tolist(), df_filtered['descripcion_promo'].tolist(),
                                               df_filtered['url_img'].tolist()))]
                    items_carousel[0]['interval'] = None
                    carousel(items=items_carousel, width=1, height=200)

                st.subheader("DataFrame Filtrado:")
                st.dataframe(df_filtered)

            with col2:
                st.subheader('Datos:')
                st.write('pass')

            col3, col4 = st.columns((0.4, 0.6), gap='small')
            with col3:
                with st.spinner('Cargando gráficos...'):
                    row1 = st.columns(1)
                    row2 = st.columns(1)
                    for col in row1:
                        tile1 = col.container(height=380)
                        tile1.markdown(f"<h1 style='text-align: left;font-size: 17px;'>WordCloud</h1>", unsafe_allow_html=True)
                        fig = plot_wordcloud(df_filtered, df_col, color='white', max_words=20)
                        tile1.pyplot(fig)
                    for col in row2:
                        tile2 = col.container(height=420)
                        with st.spinner('Cargando gráficos...'):
                            fig = plot_against_offer_type(df_filtered, df_col, top=5, height=350, width=350)
                            tile2.plotly_chart(fig, theme="streamlit")

            with col4:
                tab3, tab4 = st.tabs(["Bar Plot", "Line Plot"])
                top, height, width = (10, 600, 800)
                with tab3:
                    with st.spinner('Cargando gráficos...'):
                        fig = plot_col_against_date(df_filtered, df_col, plot_type='bar', top=top, height=height, width=width)
                        st.plotly_chart(fig, theme="streamlit")

                with tab4:
                    with st.spinner('Cargando gráficos...'):
                        fig = plot_col_against_date(df_filtered, df_col, plot_type='line', top=top, height=height, width=width)
                        st.plotly_chart(fig, theme="streamlit")
    except Exception as e:
        st.error(e)
else:
    st.write(':gear: Dashboard solo disponible para test de promociones por ahora :gear:')


