import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# =============================================================================
st.set_page_config(
    page_title="Dashboard de Desempeño - Socialize your knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. CARGA Y LIMPIEZA DE LA BASE DE DATOS
# =============================================================================
@st.cache_data
def load_data():
    path = 'Employee_data.csv'
    if os.path.exists(path):
        df_loaded = pd.read_csv(path, sep=None, engine='python', encoding='utf-8-sig')
        
        # Limpieza de espacios en blanco en los nombres de las columnas
        df_loaded.columns = df_loaded.columns.str.strip()
        
        # Limpieza de espacios en blanco dentro de las celdas de texto (Corrige el "M ")
        for col in df_loaded.select_dtypes(include=['object']).columns:
            df_loaded[col] = df_loaded[col].astype(str).str.strip()
            
        return df_loaded
    else:
        st.error("❌ Error crítico: No se encontró el archivo 'Employee_data.csv' en el repositorio.")
        st.stop()

# Cargar los datos del archivo provisto
df_raw = load_data()

# Asegurar que las columnas cuantitativas clave sean tratadas como números
df_raw['performance_score'] = pd.to_numeric(df_raw['performance_score'], errors='coerce')
df_raw['average_work_hours'] = pd.to_numeric(df_raw['average_work_hours'], errors='coerce')
df_raw['age'] = pd.to_numeric(df_raw['age'], errors='coerce')
df_raw['salary'] = pd.to_numeric(df_raw['salary'], errors='coerce')

# =============================================================================
# 3. CONTROLES DE FILTRADO INTERACTIVO (SIDEBAR)
# =============================================================================
st.sidebar.header("⚙️ Filtros de Búsqueda")

# Filtro Auxiliar: Departamento 
depts_disponibles = sorted(list(df_raw['department'].dropna().unique()))
selected_dept = st.sidebar.selectbox("Selecciona el Departamento:", ["Todos"] + depts_disponibles)

df_working = df_raw.copy()
if selected_dept != "Todos":
    df_working = df_working[df_working['department'] == selected_dept]

# Filtros principales solicitados
gender_options = ["Todos"] + sorted(list(df_working['gender'].dropna().unique()))
selected_gender = st.sidebar.selectbox("Selecciona el Género:", gender_options)

selected_perf_range = st.sidebar.slider("Rango de Puntaje de Desempeño:", min_value=1, max_value=5, value=(1, 5))

marital_options = ["Todos"] + sorted(list(df_working['marital_status'].dropna().unique()))
selected_marital = st.sidebar.selectbox("Selecciona el Estado Civil:", marital_options)

# --- APLICACIÓN DE LOS FILTROS ---
df_filtered = df_working.copy()

if selected_gender != "Todos":
    df_filtered = df_filtered[df_filtered['gender'] == selected_gender]
    
df_filtered = df_filtered[
    (df_filtered['performance_score'] >= selected_perf_range[0]) & 
    (df_filtered['performance_score'] <= selected_perf_range[1])
]

if selected_marital != "Todos":
    df_filtered = df_filtered[df_filtered['marital_status'] == selected_marital]

# =============================================================================
# 4. TÍTULO, DESCRIPCIÓN Y LOGOTIPO
# =============================================================================
st.title("📊 Dashboard de Análisis de Desempeño
