import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. CONFIGURACIÓN DE LA PÁGINA WEB
st.set_page_config(
    page_title="Dashboard Marketing - Socialize your knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CARGA Y FILTRADO DE LA BASE DE DATOS
@st.cache_data
def load_data():
    path = 'employee_data.csv'
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        # Si el archivo obligatorio no está, la app se detiene limpiamente explicando el motivo
        st.error("❌ Error crítico: No se encontró el archivo 'employee_data.csv' en el repositorio.")
        st.info("Por favor, asegúrate de subir el archivo CSV a la misma carpeta de tu repositorio en GitHub.")
        st.stop()

# Cargar datos reales
df_raw = load_data()

# Filtrar e identificar únicamente al Área de Marketing
df = df_raw[df_raw['department'].str.lower() == 'marketing'].copy()

# 3. TÍTULO, DESCRIPCIÓN Y LOGOTIPO
st.title("📊 Dashboard de Análisis de Desempeño")
st.subheader("Área de Marketing — Socialize your knowledge")

if os.path.exists('logo.png'):
    st.image('logo.png', width=180)
else:
    st.markdown("🌐 **[LOGOTIPO: Socialize your knowledge]**")

st.markdown("Esta aplicación web interactiva muestra el análisis de desempeño exclusivo de los colaboradores del **Área de Marketing**.")
st.markdown("---")

# 4. CONTROLES Y FILTROS INTERACTIVOS (Sidebar / Menú Lateral)
st.sidebar.header("⚙️ Filtros del Personal")

# Filtro A: Género
gender_options = ["Todos"] + list(df['gender'].unique())
selected_gender = st.sidebar.selectbox("Selecciona el Género:", gender_options)

# Filtro B: Rango de Puntaje de Desempeño
min_perf = int(df['performance_score'].min()) if not df.empty else 1
max_perf = int(df['performance_score'].max()) if not df.empty else 5
selected_perf_range = st.sidebar.slider("Rango de Puntaje de Desempeño:", 1, 5, (min_perf, max_perf))

# Filtro C: Estado Civil
marital_options = ["Todos"] + list(df['marital_status'].unique())
selected_marital = st.sidebar.selectbox("Selecciona el Estado Civil:", marital_options)

# Aplicar Filtros
df_filtered = df.copy()
if selected_gender != "Todos":
    df_filtered = df_filtered[df_filtered['gender'] == selected_gender]
    
df_filtered = df_filtered[
    (df_filtered['performance_score'] >= selected_perf_range[0]) & 
    (df_filtered['performance_score'] <= selected_perf_range[1])
]

if selected_marital != "Todos":
    df_filtered = df_filtered[df_filtered['marital_status'] == selected_marital]

# Validar si hay datos después de filtrar
if df_filtered.empty:
    st.error("⚠️ No se encontraron colaboradores de Marketing con los filtros seleccionados.")
else:
    # Vista previa de la matriz de datos
    with st.expander("👀 Ver registros filtrados actuales"):
        st.dataframe(df_filtered)

    # 5. VISUALIZACIÓN DE GRÁFICOS
    st.markdown("## 📈 Análisis Visual")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Distribución de los Puntajes de Desempeño")
        fig1 = px.histogram(df_filtered, x='performance_score', nbins=5, labels={'performance_score': 'Puntaje de Desempeño', 'count': 'Total Empleados'}, color_discrete_sequence=['#4A90E2'])
        fig1.update_layout(bargap=0.15)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("### ⏱️ Promedio de Horas Trabajadas por Género")
        df_hours_gender = df_filtered.groupby('gender', as_index=False)['average_work_hours'].mean()
        fig2 = px.bar(df_hours_gender, x='gender', y='average_work_hours', labels={'gender': 'Género', 'average_work_hours': 'Horas Promedio Mensuales'}, color='gender', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 💰 Edad vs. Salario de los Empleados")
        fig3 = px.scatter(df_filtered, x='age', y='salary', hover_name='name_employee', color='position', size='satisfaction_level', labels={'age': 'Edad', 'salary': 'Salario Anual ($)', 'position': 'Puesto'})
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("### 📊 Horas Trabajadas vs. Puntaje de Desempeño")
        fig4 = px.scatter(df_filtered, x='average_work_hours', y='performance_score', hover_name='name_employee', color='performance_score_desc', labels={'average_work_hours': 'Horas Mensuales Trabajadas', 'performance_score': 'Puntaje de Desempeño', 'performance_score_desc': 'Calificación'})
        st.plotly_chart(fig4, use_container_width=True)

# 6. CONCLUSIÓN DEL ANÁLISIS
st.markdown("---")
st.markdown("## 📝 Conclusión del Análisis")
st.info("""
El presente Dashboard interactivo permite evaluar de manera integral al Área de Marketing. 
A través de la segmentación dinámica, el departamento de Recursos Humanos y los líderes de equipo pueden:
* **Monitorear el Rendimiento:** Identificar qué porcentaje del equipo se encuentra en el nivel máximo de desempeño (5) y quiénes requieren capacitación.
* **Evaluar la Eficiencia:** Correlacionar el promedio de horas mensuales trabajadas con los resultados de desempeño, previniendo el *burnout*.
* **Equidad y Competitividad Salarial:** Cruzar las variables de edad y puesto respecto al salario asignado para asegurar estructuras de compensación justas.
""")
