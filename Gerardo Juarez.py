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
        
        # Limpieza de espacios en blanco dentro de las celdas de texto
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
st.title("📊 Dashboard de Análisis de Desempeño")
st.subheader(f"Análisis del Personal — Área: {selected_dept}")

if os.path.exists('logo.png'):
    st.image('logo.png', width=180)
else:
    st.markdown("🌐 **[LOGOTIPO: Socialize your knowledge]**")

st.markdown("Esta aplicación web interactiva muestra el análisis de desempeño de los colaboradores de la organización.")
st.markdown("---")

# Validación de registros resultantes
if df_filtered.empty:
    st.error("⚠️ No se encontraron colaboradores con la combinación de filtros seleccionada.")
else:
    # Vista previa de la matriz de datos actual
    with st.expander("👀 Ver matriz de registros filtrados"):
        st.dataframe(df_filtered)

    # =============================================================================
    # 5. VISUALIZACIÓN DE GRÁFICOS
    # =============================================================================
    st.markdown("## 📈 Análisis Visual")
    
       # -------------------------------------------------------------------------
    # FILA 2: Distribución de Desempeño y Horas por Género (En paralelo)
    # -------------------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
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

    st.markdown("---")

    # -------------------------------------------------------------------------
    # FILA 3: Distribución de Horas vs Desempeño (Boxplot - Standalone / Grande)
    # -------------------------------------------------------------------------
    st.markdown("### 📊 Distribución de Horas Trabajadas por Puntaje de Desempeño (Boxplot)")
    
    df_boxplot = df_filtered.copy()
    df_boxplot['performance_score'] = df_boxplot['performance_score'].astype(str)
    
    fig4 = px.box(
        df_boxplot, 
        x='performance_score', 
        y='average_work_hours',
        color='performance_score',
        points="all", 
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={
            'performance_score': 'Puntaje de Desempeño', 
            'average_work_hours': 'Horas Mensuales Trabajadas'
        }
    )
    fig4.update_layout(height=500) # Ajuste de altura para mayor visibilidad
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # -------------------------------------------------------------------------
    # FILA 4: Edad vs Salario (Scatter - Standalone / Grande debajo del Boxplot)
    # -------------------------------------------------------------------------
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
    fig3.update_layout(height=550) # Altura optimizada para el mapa de dispersión
    st.plotly_chart(fig3, use_container_width=True)

# =============================================================================
# 6. SECCIÓN: CONCLUSIÓN DEL ANÁLISIS MOSTRADO
# =============================================================================
st.markdown("---")
st.markdown("## 📝 Conclusión del Análisis")
st.info(f"""
El presente Dashboard interactivo permite evaluar de manera integral el desempeño organizacional en **Socialize your knowledge**. 
Basado en los filtros activos del departamento seleccionado ({selected_dept}), se concluye lo siguiente:

* **Diversidad e Inclusión:** La gráfica de distribución por género expone de manera visual e inmediata el balance demográfico de los equipos corporativos facilitando auditorías de equidad.
* **Monitorear el Rendimiento:** La distribución de los puntajes permite mapear con precisión qué porcentaje del equipo se ubica en categorías sobresalientes versus aquellos que requieren capacitaciones estructuradas.
* **Análisis Estadístico de Eficiencia (Boxplot):** El diagrama de cajas permite analizar visualmente la dispersión, las medianas y los valores atípicos de las horas mensuales trabajadas contra las calificaciones de desempeño obtenidas, permitiendo identificar si un exceso de horas trabajadas verdaderamente impacta de forma positiva en la calificación del colaborador.
* **Equidad y Competitividad Salarial:** El análisis cruzado a gran escala de edad, puesto y salario proporciona visibilidad clave para garantizar políticas de compensación justas, transparentes y competitivas en el mercado.
""")
