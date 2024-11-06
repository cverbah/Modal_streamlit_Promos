import streamlit as st
import pandas as pd
import os
import numpy as np
from utils import parse_null_list
from streamlit_extras.app_logo import add_logo
from ast import literal_eval


st.set_page_config(
    page_title="App Promociones",
    page_icon=":robot_face:",
    layout="wide",
)
st.title('Análisis de promociones')

uploaded_file = st.file_uploader("Seleccione un archivo CSV con el retail a analizar", type=["csv"])

try:
    if uploaded_file:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, } #"FileSize": uploaded_file.size
        st.write(file_details)

        # save file as temp.csv
        with open("temp.csv", "wb") as f:
            f.write(uploaded_file.getvalue())
        temp_location = os.path.abspath("temp.csv")

        # read uploaded csv file adn store as dataframe
        if 'df' not in st.session_state:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(temp_location, index_col=0)
                st.session_state.df = df

        st.subheader("DataFrame:")
        st.dataframe(st.session_state.df)

except Exception as e:
    st.error(f"Error: {e}. Check your uploaded dataset")
