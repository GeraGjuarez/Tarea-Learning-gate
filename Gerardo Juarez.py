import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# =============================================================================
st.set_page_config(
    page_title="Dashboard Marketing - Socialize your knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. CARGA Y LIMPIEZA DE LA BASE DE DATOS
# =============================================================================
@st.cache_data
def load_data():
    path = 'employee_data.csv'
    if os.path.exists(path):
        # sep=None detecta automáticamente si el CSV usa comas o puntos y comas
        df_loaded = pd.read_csv(path, sep=None, engine='python', encoding='utf-8-sig')
        # Limpiar espacios ocultos en los nombres de las columnas
        df_loaded.columns = df_loaded.columns.str.strip()
        return df_loaded
    else:
        st.error("❌ Error: No se encontró el archivo 'employee_data.csv' en tu repositorio.")
        st.stop()

# Cargar los datos reales
df_raw = load_data()

# Validar que existan las columnas esenciales antes de avanzar
columnas_requeridas = ['department', 'gender', 'performance_score', 'marital_status', 'average_work_hours', 'age', 'salary']
columnas_faltantes = [col for col in columnas_requeridas if col not in df_raw.columns]

if columnas_faltantes:
    st.error(f"❌ Al archivo CSV le faltan las siguientes columnas obligatorias: {columnas_faltantes}")
    st.info(f"Columnas detectadas en tu archivo: {list(df_raw.columns)}")
    st.stop()

# --- salvaguarda de tipos de datos ---
# Convertimos a números de forma segura. Si hay textos extraños o celdas vacías, los maneja sin romper la app
df_raw['performance_score'] = pd.to_numeric(df_raw['performance_score'], errors='coerce')
df_raw['average_work_hours'] = pd.to_numeric(df_raw['average_work_hours'], errors='coerce')
df_raw['age'] = pd.to_numeric(df_raw['age'], errors='coerce')
df_raw['salary'] = pd.to_numeric(df_raw['salary'], errors='coerce')

# Filtrar para dejar ÚNICAMENTE al Área de Marketing
df = df_raw[df_raw['department'].astype(str).str.strip().str.lower() == 'marketing'].copy()

# Si el filtro de Marketing se queda vacío, mostramos ayuda en pantalla
if df.empty:
    st.warning("⚠️ El archivo cargó correctamente, pero ningún empleado tiene asignado el departamento exacto de 'Marketing'.")
    st.info("Revisa qué departamentos detectó el sistema dentro de tu archivo actual:")
    st.write(list(df_raw['department'].dropna().unique()))
    st.stop()

# =============================================================================
# 3. TÍTULO, DESCRIPCIÓN Y LOGOTIPO
# =============================================================================
st.title("📊 Dashboard de Análisis de Desempeño")
st.subheader("Área de Marketing — Socialize your knowledge")

if os.path.exists('logo.png'):
    st.image('logo.png', width=180)
else:
    st.markdown("🌐 **[LOGOTIPO: Socialize your knowledge]**")

st.markdown("Esta aplicación web interactiva muestra el análisis de desempeño exclusivo de los colaboradores del **Área de Marketing**.")
st.markdown("---")

# =============================================================================
# 4. CONTROLES Y FILTROS INTERACTIVOS (Sidebar / Menú Lateral)
# =============================================================================
st.sidebar.header("⚙️ Filtros del Personal")

# Filtro A: Género
gender_options = ["Todos"] + list(df['gender'].dropna().unique())
selected_gender = st.sidebar.selectbox("Selecciona el Género:", gender_options)

# Filtro B: Rango de Puntaje de Desempeño (Rango fijo seguro de 1 a 5 para evitar desbordamientos)
selected_perf_range = st.sidebar.slider("Rango de Puntaje de Desempeño:", min_value=1, max_value=5, value=(1, 5))

# Filtro C: Estado Civil
marital_options = ["Todos"] + list(df['marital_status'].dropna().unique())
selected_marital = st.sidebar.selectbox("Selecciona el Estado Civil:", marital_options)

# --- APLICACIÓN DE LOS FILTROS ---
df_filtered = df.copy()
if selected_gender != "Todos":
    df_filtered = df_filtered[df_filtered['gender'] == selected_gender]
    
df_filtered = df_filtered[
    (df_filtered['performance_score'] >= selected_perf_range[0]) & 
    (df_filtered['performance_score'] <= selected_perf_range[1])
]

if selected_marital != "Todos":
    df_filtered = df_filtered[df_filtered['marital_status'] == selected_marital]

# Validar si hay datos después de usar los filtros
if df_filtered.empty:
    st.error("⚠️ No se encontraron colaboradores de Marketing con la combinación de filtros seleccionada.")
else:
    # Vista previa de la matriz de datos filtrados
    with st.expander("👀 Ver registros filtrados actuales"):
        st.dataframe(df_filtered)

    # =============================================================================
    # 5. VISUALIZACIÓN DE GRÁFICOS
    # =============================================================================
    st.markdown("## 📈 Análisis Visual")
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico 1: Distribución de los puntajes de desempeño
        st.markdown("### 🎯 Distribución de los Puntajes de Desempeño")
        fig1 = px.histogram(df_filtered, x='performance_score', nbins=5, 
                             labels={'performance_score': 'Puntaje de Desempeño', 'count': 'Total Empleados'}, 
                             color_discrete_sequence=['#4A90E2'])
        fig1.update_layout(bargap=0.15)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Gráfico 2: Promedio de horas trabajadas por el género del empleado
        st.markdown("### ⏱️ Promedio de Horas Trabajadas por Género")
        df_hours_gender = df_filtered.groupby('gender', as_index=False)['average_work_hours'].mean()
        fig2 = px.bar(df_hours_gender, x='gender', y='average_work_hours', 
                      labels={'gender': 'Género', 'average_work_hours': 'Horas Promedio Mensuales'}, 
                      color='gender', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Gráfico 3: Edad de los empleados con respecto al salario de los mismos
        st.markdown("### 💰 Edad vs. Salario de los Empleados")
        fig3 = px.scatter(df_filtered, x='age', y='salary', hover_name='name_employee', 
                          color='position', size='satisfaction_level', 
                          labels={'age': 'Edad', 'salary': 'Salario ($)', 'position': 'Puesto'})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # Gráfico 4: Relación del promedio de horas trabajadas vs. el puntaje de desempeño
        st.markdown("### 📊 Horas Trabajadas vs. Puntaje de Desempeño")
        fig4 = px.scatter(df_filtered, x='average_work_hours', y='performance_score', 
                          hover_name='name_employee', color='performance_score_desc', 
                          labels={'average_work_hours': 'Horas Mensuales Trabajadas', 
                                  'performance_score': 'Puntaje de Desempeño', 
                                  'performance_score_desc': 'Calificación'})
        st.plotly_chart(fig4, use_container_width=True)

# =============================================================================
# 6. CONCLUSIÓN DEL ANÁLISIS
# =============================================================================
st.markdown("---")
st.markdown("## 📝 Conclusión del Análisis")
st.info("""
El presente Dashboard interactivo permite evaluar de manera integral al Área de Marketing. 
A través de la segmentación dinámica, el departamento de Recursos Humanos y los líderes de equipo pueden:
* **Monitorear el Rendimiento:** Identificar qué porcentaje del equipo se encuentra en el nivel máximo de desempeño (5) y quiénes requieren capacitación o soporte.
* **Evaluar la Eficiencia:** Correlacionar el promedio de horas mensuales trabajadas con los resultados de desempeño, previniendo el *burnout*.
* **Equidad y Competitividad Salarial:** Cruzar las variables de edad y puesto respecto al salario asignado para asegurar estructuras de compensación justas.
""")
