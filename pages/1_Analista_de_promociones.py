import streamlit as st
from utils import *
from utils_plots import plot_wordcloud, plot_against_offer_type
import pandas as pd
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

st.set_page_config(
    page_title="Analista Promociones",
    page_icon=":robot_face:",
    layout="wide",
)

st.title(':robot_face: Analista de  Promociones')

try:
    with st.spinner('Cargando datos...'):
        df = st.session_state.df
        df_filtered = pd.DataFrame()

    if 'df_with_promo' not in st.session_state:
        st.session_state.df_with_promo = False

    if st.session_state.df_with_promo:
        with st.sidebar:
            st.title(':gear: Filtros')
            st.subheader('Tabla:')
            # offer filters
            offer_type = df['tipo_oferta'].unique().tolist()
            offer_type.extend(['todas'])
            select_offer = st.selectbox('Seleccione el tipo de oferta:', offer_type, index=len(offer_type) - 1)

            st.subheader('Gráfico:')
            # column filter
            col_types = ['categorias_en_promo', 'marcas_en_promo', 'publico_objetivo']
            df_col = st.selectbox('Seleccione la columna que desea gráficar:', col_types, index=1)

            # dataframe filter
            if select_offer:

                if select_offer != 'todas':
                    df_filtered = df[(df.tipo_oferta == select_offer)].reset_index(drop=True)
                else:
                    df_filtered = df.reset_index(drop=True)
                #df_filtered.drop(columns=['datetime_checked'], inplace=True)

    if (len(st.session_state.df) > 0) & (st.session_state.df_with_promo == False):
        st.markdown("<span style='font-size: 20px;'>1 - Aprete el botón para comenzar análisis de promociones</span>",
                    unsafe_allow_html=True)

        if st.button('Analizar'):
            with st.spinner('Analizando promociones ...'):
                st.session_state.df['promo_analysis'] = st.session_state.df['url_img'].apply(lambda row:
                                                                                             analyze_promo_v2(row,
                                                                                                              format=True))
                analyze_data(st.session_state.df)
                st.subheader("DataFrame:")
                #st.dataframe(st.session_state.df)
                st.session_state.df_with_promo = True
                if len(df_filtered) > 0:
                    st.dataframe(df_filtered)
                else:
                    st.dataframe(st.session_state.df)
                st.rerun()

    elif st.session_state.df_with_promo:
        st.subheader("DataFrame con ofertas analizadas:")
        if len(df_filtered) > 0:
            st.dataframe(df_filtered)
        else:
            st.dataframe(st.session_state.df)

        tab1, tab2 = st.tabs(["Imágenes Promociones", "Gáficos"])

        with tab1:
            st.subheader("Imágenes promociones:")
            promotions = df_filtered['nombre_promocion'].tolist()
            select_promotion = st.selectbox('Seleccione la promoción:', promotions, index=0)
            url_image = df[df['nombre_promocion'] == select_promotion].url_img.tolist()[0]
            st.write(url_image)
            try:
                # Load image from URL
                response = requests.get(url_image)
                img = Image.open(BytesIO(response.content))

            except UnidentifiedImageError:
                st.error("The file is not a valid image or is corrupted. Please upload a valid image file.")

            except Exception as e:
                st.error(f"An error occurred: {e}")

            width, height = img.size
            img_dims = f"Img size: {width}x{height} pixels"
            img_aux = False
            if width > 2000:
                img_aux = True

            st.image(img, caption=f"Promoción: {select_promotion}. {img_dims}", use_column_width=img_aux)

        with tab2:
            rows = st.columns(2)
            grid = [col.container(height=500) for col in rows]
            df_filtered_problems = df_filtered.dropna(subset=['descripcion_promo'])
            with grid[0]:
                with st.spinner('Cargando gráficos...'):
                    st.markdown(f"<h1 style='text-align: left;font-size: 17px;'>WordCloud: {df_col}</h1>",
                                unsafe_allow_html=True)

                    fig = plot_wordcloud(df_filtered_problems, df_col, color='white', max_words=20)
                    st.pyplot(fig)
            with grid[1]:
                with st.spinner('Cargando gráficos...'):
                    fig = plot_against_offer_type(df_filtered_problems, df_col, top=10, height=450, width=600)
                    st.plotly_chart(fig, theme="streamlit")

    else:
        st.warning('Tabla cargada no contiene datos. Intente de nuevo con otra tabla')



except Exception as e:
    st.error(f"An error occurred: {e}")
