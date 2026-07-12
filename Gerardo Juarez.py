import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =============================================================================
# SECCIÓN: CONFIGURACIÓN DE LA PÁGINA WEB
# =============================================================================
st.set_page_config(
    page_title="Dashboard de Desempeño - Socialize your knowledge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SECCIÓN: CARGA Y LIMPIEZA AUTOMÁTICA DE LA BASE DE DATOS
# =============================================================================
@st.cache_data
def load_data():
    path = 'Employee_data.csv'
    if os.path.exists(path):
        # Lee el archivo detectando automáticamente el separador (, o ;)
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
# SECCIÓN: TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN WEB
# =============================================================================
st.title(" 📊 Dashboard de Análisis de Desempeño")
st.subheader("Plataforma Corporativa — Socialize your knowledge")

st.markdown("""
Esta aplicación web interactiva permite evaluar el desempeño, salarios y jornadas laborales de los colaboradores. 
Utiliza el menú de la izquierda para segmentar los datos en tiempo real.
""")

# =============================================================================
# SECCIÓN: DESPLIEGUE DEL LOGOTIPO DE LA EMPRESA
# =============================================================================
if os.path.exists('logo.png'):
    st.image('logo.png', width=180)
else:
    st.markdown("🌐 **[LOGOTIPO: Socialize your knowledge]**")

st.markdown("---")

# =============================================================================
# SECCIÓN: CONTROLES DE FILTRADO INTERACTIVO (SIDEBAR)
# =============================================================================
st.sidebar.header("⚙️ Filtros de Búsqueda")

# Filtro Auxiliar: Departamento (Permite al evaluador navegar por los datos reales del archivo)
depts_disponibles = sorted(list(df_raw['department'].dropna().unique()))
selected_dept = st.sidebar.selectbox("Selecciona el Departamento:", ["Todos"] + depts_disponibles)

df_working = df_raw.copy()
if selected_dept != "Todos":
    df_working = df_working[df_working['department'] == selected_dept]

# 1. Control para seleccionar el GÉNERO del empleado
gender_options = ["Todos"] + sorted(list(df_working['gender'].dropna().unique()))
selected_gender = st.sidebar.selectbox("Selecciona el Género:", gender_options)

# 2. Control para seleccionar un RANGO del PUNTAJE DE DESEMPEÑO (1 a 5)
selected_perf_range = st.sidebar.slider("Rango de Puntaje de Desempeño:", min_value=1, max_value=5, value=(1, 5))

# 3. Control para seleccionar el ESTADO CIVIL del empleado
marital_options = ["Todos"] + sorted(list(df_working['marital_status'].dropna().unique()))
selected_marital = st.sidebar.selectbox("Selecciona el Estado Civil:", marital_options)

# --- APLICACIÓN DE LOS FILTROS SELECCIONADOS ---
df_filtered = df_working.copy()

if selected_gender != "Todos":
    df_filtered = df_filtered[df_filtered['gender'] == selected_gender]
    
df_filtered = df_filtered[
    (df_filtered['performance_score'] >= selected_perf_range[0]) & 
    (df_filtered['performance_score'] <= selected_perf_range[1])
]

if selected_marital != "Todos":
    df_filtered = df_filtered[df_filtered['marital_status'] == selected_marital]

# Validación de registros resultantes
if df_filtered.empty:
    st.error("⚠️ No se encontraron colaboradores con la combinación de filtros seleccionada.")
else:
    # Vista previa de la matriz de datos actual
    with st.expander("👀 Ver matriz de registros filtrados"):
        st.dataframe(df_filtered)

    # =============================================================================
    # SECCIÓN: VISUALIZACIÓN DE GRÁFICOS
    # =============================================================================
    st.markdown("## 📈 Análisis Visual")
    col1, col2 = st.columns(2)

    with col1:
        # A. Visualización de la distribución de los puntajes de desempeño
        st.markdown("### 🎯 Distribución de los Puntajes de Desempeño")
        fig1 = px.histogram(
            df_filtered, 
            x='performance_score', 
            nbins=5, 
            labels={'performance_score': 'Puntaje de Desempeño', 'count': 'Frecuencia'}, 
            color_discrete_sequence=['#4A90E2']
        )
        fig1.update_layout(bargap=0.15)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # B. Visualización del promedio de horas trabajadas por el género del empleado
        st.markdown("### ⏱️ Promedio de Horas Trabajadas por Género")
        df_hours_gender = df_filtered.groupby('gender', as_index=False)['average_work_hours'].mean()
        fig2 = px.bar(
            df_hours_gender, 
            x='gender', 
            y='average_work_hours', 
            labels={'gender': 'Género', 'average_work_hours': 'Horas Promedio'}, 
            color='gender', 
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # C. Visualización de la edad de los empleados con respecto al salario de los mismos
        st.markdown("### 💰 Edad vs. Salario de los Empleados")
        fig3 = px.scatter(
            df_filtered, 
            x='age', 
            y='salary', 
            hover_name='name_employee', 
            color='position', 
            size='satisfaction_level', 
            labels={'age': 'Edad', 'salary': 'Salario ($)', 'position': 'Puesto'}
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        # D. Visualización de la relación del promedio de horas trabajadas versus el puntaje de desempeño
        st.markdown("### 📊 Horas Trabajadas vs. Puntaje de Desempeño")
        fig4 = px.scatter(
            df_filtered, 
            x='average_work_hours', 
            y='performance_score', 
            hover_name='name_employee', 
            color='performance_score_desc', 
            labels={
                'average_work_hours': 'Horas Trabajadas', 
                'performance_score': 'Puntaje de Desempeño', 
                'performance_score_desc': 'Calificación'
            }
        )
        st.plotly_chart(fig4, use_container_width=True)

# =============================================================================
# SECCIÓN: CONCLUSIÓN DEL ANÁLISIS MOSTRADO
# =============================================================================
st.markdown("---")
st.markdown("## 📝 Conclusión del Análisis")
st.info(f"""
El presente Dashboard interactivo permite evaluar de manera integral el desempeño organizacional en **Socialize your knowledge**. 
Basado en los filtros activos del departamento seleccionado ({selected_dept}), se concluye lo siguiente:

* **Monitorear el Rendimiento:** La distribución de los puntajes permite mapear con precisión qué porcentaje del equipo se ubica en categorías sobresalientes versus aquellos que requieren capacitaciones estructuradas.
* **Evaluar la Eficiencia:** Al correlacionar las horas mensuales trabajadas con los puntajes de rendimiento, la empresa puede identificar patrones de alta productividad y mitigar riesgos de desgaste laboral o *burnout*.
* **Equidad y Competitividad Salarial:** El análisis cruzado de edad, puesto y salario proporciona visibilidad clave para garantizar políticas de compensación justas, transparentes y competitivas en el mercado.
""")
