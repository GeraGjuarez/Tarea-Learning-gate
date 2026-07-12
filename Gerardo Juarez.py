import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Dashboard Marketing - Socialize your knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CARGA Y FILTRADO DE LA BASE DE DATOS (Con tus nuevas columnas)
# =============================================================================
@st.cache_data
def load_data():
    path = 'employee_data.csv'
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df
    else:
        # Datos simulados con la estructura EXACTA de tu Excel para pruebas locales
                return pd.DataFrame(data)

# Cargar base de datos
df_raw = load_data()

)
