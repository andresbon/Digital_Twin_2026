import streamlit as st
import sys
# Inyectar la clase DigitalTwinBundle en __main__ para que joblib pueda encontrarla
from bundle_schema import DigitalTwinBundle
if hasattr(sys.modules['__main__'], '__dict__'):
    sys.modules['__main__'].DigitalTwinBundle = DigitalTwinBundle
import plotly.graph_objects as go
import pandas as pd
from risk_engine import predict_all_risks
from clinical_scenarios import get_all_scenarios, get_scenario_details
from config import is_openai_configured
from ai_interpreter import generate_clinical_interpretation, generate_scenario_comparison

# Configuración de página mejorada
st.set_page_config(
    layout="wide",
    page_title="Monitor de Riesgo Renal",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com',
        'About': "Monitor Digital Twin para Predicción de Riesgos Renales v1.0"
    }
)

# CSS personalizado para mejorar la presentación
st.markdown("""
<style>
    /* Variables de colores */
    :root {
        --primary-color: #1f77d2;
        --success-color: #2ecc71;
        --warning-color: #f39c12;
        --danger-color: #e74c3c;
        --secondary-color: #34495e;
    }
    
    /* Estilos generales */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Mejora de título */
    h1 {
        color: #1f77d2;
        padding: 20px 0;
        border-bottom: 3px solid #1f77d2;
        margin-bottom: 30px;
        font-weight: 700;
    }
    
    h2 {
        color: #2c3e50;
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    h3 {
        color: #34495e;
        margin-top: 20px;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    /* Estilos de cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #1f77d2;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Sidebar mejorada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(90deg, #1f77d2 0%, #1568c7 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #1568c7 0%, #0f5db5 100%);
        box-shadow: 0 4px 12px rgba(31, 119, 210, 0.3);
        transform: translateY(-2px);
    }
    
    /* Checkboxes mejorados */
    .stCheckbox {
        margin: 8px 0;
    }
    
    /* Selectores mejorados */
    .stSelectbox, .stSlider, .stMultiSelect {
        margin: 12px 0;
    }
    
    /* Mensajes de información */
    .stInfo {
        background-color: rgba(31, 119, 210, 0.1);
        border-left: 4px solid #1f77d2;
        border-radius: 4px;
        padding: 12px 16px;
    }
    
    .stSuccess {
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 4px solid #2ecc71;
    }
    
    .stWarning {
        background-color: rgba(243, 156, 18, 0.1);
        border-left: 4px solid #f39c12;
    }
    
    .stError {
        background-color: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;
    }
    
    /* Tabs mejoradas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-testid="stTab"] {
        padding: 12px 20px;
        font-weight: 500;
        border-radius: 6px 6px 0 0;
    }
    
    /* Tablas */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Separadores */
    hr {
        margin: 30px 0;
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ddd, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Título principal con estilo mejorado
st.markdown("""
# 🧬 Panel de Control Digital Twin
## Monitor de Riesgo Renal
""")

# Banner de configuración de OpenAI si no está configurado
if not is_openai_configured():
    with st.info(""):
        st.markdown("""
        ### 🔑 Configuración de OpenAI API
        
        Para habilitar **análisis clínicos mejorados con IA**, configura tu API key:
        
        1. **Obtén tu API key**: https://platform.openai.com/account/api-keys
        2. **Crea un archivo `.env`** en la raíz del proyecto
        3. **Reinicia la aplicación**
        
        📖 **Leer guía completa**: Ver archivo `SETUP.md`
        """)
else:
    st.success("✅ OpenAI API configurada correctamente")

# Opciones en la barra lateral
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configuración de la Aplicación")

# Crear pestañas para diferentes funcionalidades
tab1, tab2 = st.tabs(["📊 Predicción Individual", "📈 Análisis Comparativo"])

with tab1:
    st.sidebar.header("📋 Datos Clínicos del Paciente")
    
    # Opción para usar escenario predefinido o entrada manual
    use_scenario = st.sidebar.checkbox("Usar escenario predefinido", value=False)
    
    if use_scenario:
        scenario_name = st.sidebar.selectbox("Selecciona un escenario", list(get_all_scenarios().keys()))
        patient_data = get_scenario_details(scenario_name)
        st.sidebar.info(f"**Descripción**: {get_all_scenarios()[scenario_name]['description']}")
        
        # Extraer variables para usarlas en recomendaciones
        hypertension = patient_data.get("hypertension_flag", 0) == 1
        diabetes = patient_data.get("diabetes_flag", 0) == 1
        ckd = patient_data.get("ckd_flag", 0) == 1
    else:
        # Información del paciente
        st.sidebar.subheader("Información Demográfica")
        gender = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
        age = st.sidebar.slider("Edad", 18, 100, 60)
        anchor_year_group = st.sidebar.selectbox("Grupo de Año", ["2008-2012", "2013-2017", "2018-2022"])
        
        st.sidebar.subheader("Historial Médico")
        hypertension = st.sidebar.checkbox("Hipertensión", value=False)
        diabetes = st.sidebar.checkbox("Diabetes", value=False)
        ckd = st.sidebar.checkbox("Enfermedad Renal Crónica", value=False)
        
        st.sidebar.subheader("Parámetros Laborales")
        creatinine = st.sidebar.slider("Creatinina (mg/dL)", 0.5, 5.0, 1.2)
        bun = st.sidebar.slider("BUN (mg/dL)", 5, 100, 20)
        sodium = st.sidebar.slider("Sodio (mEq/L)", 120, 160, 138)
        potassium = st.sidebar.slider("Potasio (mEq/L)", 2.5, 7.0, 4.0)
        hemoglobin = st.sidebar.slider("Hemoglobina (g/dL)", 5.0, 18.0, 11.0)
        
        st.sidebar.subheader("Signos Vitales")
        sbp = st.sidebar.slider("Presión Arterial Sistólica (mmHg)", 60, 220, 120)
        dbp = st.sidebar.slider("Presión Arterial Diastólica (mmHg)", 30, 150, 80)
        heart_rate = st.sidebar.slider("Frecuencia Cardíaca (bpm)", 30, 200, 80)
        
        patient_data = {
            "gender": 1 if gender == "Masculino" else 0,
            "age": age,
            "anchor_year_group": ["2008-2012", "2013-2017", "2018-2022"].index(anchor_year_group),
            "hypertension_flag": 1 if hypertension else 0,
            "diabetes_flag": 1 if diabetes else 0,
            "ckd_flag": 1 if ckd else 0,
            "creatinine": creatinine,
            "bun": bun,
            "sodium": sodium,
            "potassium": potassium,
            "hemoglobin": hemoglobin,
            "sbp_mean": sbp,
            "dbp_mean": dbp,
            "heart_rate_mean": heart_rate,
        }
    
    # Agregar espacio y botón para hacer la predicción
    st.sidebar.markdown("---")
    
    # Inicializar estado de predicción
    if "show_predictions" not in st.session_state:
        st.session_state.show_predictions = False
    
    if st.sidebar.button("🔮 Predecir Condición del Paciente", use_container_width=True):
        st.session_state.show_predictions = True
    
    # Mostrar resultados si se ha hecho clic en el botón
    if st.session_state.show_predictions:
        risks = predict_all_risks(patient_data)
        
        aki = risks.get("aki_severe", {}).get("probability", 0)
        rrt = risks.get("rrt_needed", {}).get("probability", 0)
        mortality = risks.get("in_hospital_mortality", {}).get("probability", 0)
        
        # Diseño mejorado de resultados
        st.markdown("---")
        st.markdown("## 📊 Resultados de la Predicción")
        
        # Cards de métricas mejoradas
        col1, col2, col3 = st.columns(3, gap="medium")
        
        # Determinar colores basados en riesgo
        def get_risk_color(value):
            if value < 0.3:
                return "#2ecc71"  # Verde
            elif value < 0.7:
                return "#f39c12"  # Naranja
            else:
                return "#e74c3c"  # Rojo
        
        with col1:
            st.metric(
                label="🔴 Lesión Renal Aguda",
                value=f"{aki:.2%}",
                delta=None,
                delta_color="off"
            )
            if aki < 0.3:
                st.caption("✅ Riesgo bajo")
            elif aki < 0.7:
                st.caption("⚠️ Riesgo moderado")
            else:
                st.caption("❌ Riesgo alto")
        
        with col2:
            st.metric(
                label="💧 Terapia de Reemplazo",
                value=f"{rrt:.2%}",
                delta=None,
                delta_color="off"
            )
            if rrt < 0.3:
                st.caption("✅ Probabilidad baja")
            elif rrt < 0.7:
                st.caption("⚠️ Probabilidad moderada")
            else:
                st.caption("❌ Probabilidad alta")
        
        with col3:
            st.metric(
                label="⚠️ Mortalidad",
                value=f"{mortality:.2%}",
                delta=None,
                delta_color="off"
            )
            if mortality < 0.3:
                st.caption("✅ Riesgo bajo")
            elif mortality < 0.7:
                st.caption("⚠️ Riesgo moderado")
            else:
                st.caption("❌ Riesgo alto")
        
        # Gráfico mejorado
        st.markdown("### 📈 Distribución Comparativa de Riesgos")
        
        # Crear figura con dos gráficos
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            # Gráfico de barras
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                x=["AKI", "RRT", "Mortalidad"],
                y=[aki, rrt, mortality],
                marker=dict(
                    color=[get_risk_color(aki), get_risk_color(rrt), get_risk_color(mortality)],
                    line=dict(color='white', width=2)
                ),
                text=[f"{aki:.1%}", f"{rrt:.1%}", f"{mortality:.1%}"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Riesgo: %{y:.2%}<extra></extra>",
            ))
            
            fig_bar.update_layout(
                title="Riesgos por Tipo",
                xaxis_title="",
                yaxis_title="Probabilidad",
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1]),
                height=400,
                hovermode="x unified",
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_graph2:
            # Gráfico de gauge/indicador
            fig_gauge = go.Figure()
            
            # Calcular riesgo promedio
            avg_risk = (aki + rrt + mortality) / 3
            
            fig_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=avg_risk * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Riesgo Promedio"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': get_risk_color(avg_risk)},
                    'steps': [
                        {'range': [0, 30], 'color': "rgba(46, 204, 113, 0.2)"},
                        {'range': [30, 70], 'color': "rgba(243, 156, 18, 0.2)"},
                        {'range': [70, 100], 'color': "rgba(231, 76, 60, 0.2)"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 2},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=400,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Interpretación de riesgos mejorada
        st.markdown("---")
        st.markdown("### 💡 Interpretación Clínica")
        
        # Cards de interpretación mejoradas
        col_inter1, col_inter2, col_inter3 = st.columns(3, gap="medium")
        
        with col_inter1:
            st.markdown("#### 🔴 Lesión Renal Aguda")
            if aki < 0.3:
                st.success("**Riesgo Bajo**\n\nProbabilidad baja de desarrollar AKI severa")
            elif aki < 0.7:
                st.warning("**Riesgo Moderado**\n\nMonitoreo recomendado de función renal")
            else:
                st.error("**Riesgo Alto**\n\nRequiere intervención inmediata")
        
        with col_inter2:
            st.markdown("#### 💧 Terapia de Reemplazo")
            if rrt < 0.3:
                st.success("**Probabilidad Baja**\n\nNo requiere reemplazo renal en corto plazo")
            elif rrt < 0.7:
                st.warning("**Probabilidad Moderada**\n\nConsiderar monitoreo de función renal")
            else:
                st.error("**Probabilidad Alta**\n\nPreparación para RRT posiblemente necesaria")
        
        with col_inter3:
            st.markdown("#### ⚠️ Mortalidad")
            if mortality < 0.3:
                st.success("**Riesgo Bajo**\n\nPronóstico favorable")
            elif mortality < 0.7:
                st.warning("**Riesgo Moderado**\n\nMonitoreo intensivo recomendado")
            else:
                st.error("**Riesgo Alto**\n\nRequiere cuidados intensivos")
        
        # Recomendaciones clínicas
        st.markdown("### 📋 Recomendaciones de Seguimiento")
        
        rec_cols = st.columns(2, gap="medium")
        
        with rec_cols[0]:
            st.markdown("#### Monitoreo Recomendado")
            recommendations = []
            if aki > 0.5:
                recommendations.append("✓ Monitoreo diario de creatinina y BUN")
            if rrt > 0.5:
                recommendations.append("✓ Valorar necesidad de nefrología")
            if mortality > 0.5:
                recommendations.append("✓ Cuidados intensivos considerados")
            if diabetes:
                recommendations.append("✓ Optimizar control glucémico")
            if hypertension:
                recommendations.append("✓ Optimizar control presión arterial")
            
            if recommendations:
                for rec in recommendations:
                    st.write(rec)
            else:
                st.success("Seguimiento rutinario recomendado")
        
        with rec_cols[1]:
            st.markdown("#### Información al Paciente")
            st.info("""
            - Mantener hidratación adecuada
            - Seguir dieta recomendada por nutricionista
            - Tomar medicamentos según prescripción
            - Reportar síntomas: hinchazón, fatiga
            - Seguimiento de laboratorios según plan
            """)
        
        # Análisis con IA si está configurado
        if is_openai_configured():
            with st.spinner("⏳ Generando análisis clínico detallado con IA..."):
                ai_interpretation = generate_clinical_interpretation(patient_data, risks)
                
                if ai_interpretation:
                    st.markdown(ai_interpretation)
                else:
                    st.error("❌ No se pudo generar el análisis con IA en este momento. Verifica tu API key.")
        else:
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                st.info("💡 Configura OpenAI para análisis mejorados")
            with col_ai2:
                st.caption("Lee SETUP.md para instrucciones de configuración")
    else:
        st.info("👈 **Paso 1:** Ajusta los parámetros clínicos en la barra lateral\n\n👈 **Paso 2:** Haz clic en el botón para obtener las predicciones")


with tab2:
    st.markdown("# 📈 Análisis Comparativo de Escenarios")
    
    st.markdown("""
    Compara los perfiles de riesgo entre diferentes escenarios clínicos para entender cómo 
    las comorbilidades (diabetes, hipertensión, enfermedad renal crónica) afectan los resultados clínicos.
    """)
    
    st.markdown("---")
    
    # Seleccionar qué escenarios comparar
    all_scenarios = list(get_all_scenarios().keys())
    
    col_select1, col_select2 = st.columns([3, 1])
    with col_select1:
        selected_scenarios = st.multiselect(
            "Selecciona escenarios para comparar:",
            all_scenarios,
            default=all_scenarios if len(all_scenarios) <= 4 else all_scenarios[:4]
        )
    with col_select2:
        st.markdown("")
        st.markdown("")
        execute_analysis = st.button("🔄 Analizar", use_container_width=True, key="comparative_btn")
    
    if execute_analysis and selected_scenarios:
        # Obtener predicciones para cada escenario
        results_data = {
            "Escenario": [],
            "AKI": [],
            "RRT": [],
            "Mortalidad": []
        }
        
        with st.spinner("⏳ Calculando predicciones para todos los escenarios..."):
            for scenario_name in selected_scenarios:
                scenario_data = get_scenario_details(scenario_name)
                risks = predict_all_risks(scenario_data)
                
                results_data["Escenario"].append(scenario_name.split(". ")[1])
                results_data["AKI"].append(risks.get("aki_severe", {}).get("probability", 0))
                results_data["RRT"].append(risks.get("rrt_needed", {}).get("probability", 0))
                results_data["Mortalidad"].append(risks.get("in_hospital_mortality", {}).get("probability", 0))
        
        # Crear DataFrame
        df_results = pd.DataFrame(results_data)
        
        # Sección de resultados
        st.markdown("---")
        st.markdown("## 📊 Resultados del Análisis")
        
        # Tabla de resultados mejorada
        st.markdown("### 📋 Tabla Comparativa de Riesgos")
        
        colored_df = df_results.copy()
        st.dataframe(
            colored_df.style.format({
                "AKI": "{:.2%}",
                "RRT": "{:.2%}",
                "Mortalidad": "{:.2%}"
            }).background_gradient(
                subset=["AKI", "RRT", "Mortalidad"],
                cmap="RdYlGn_r",
                vmin=0,
                vmax=1
            ),
            use_container_width=True,
            height=300
        )
        
        # Gráficos comparativos mejorados
        st.markdown("### 📈 Visualización de Riesgos")
        
        # Crear dos columnas para gráficos
        col_graph1, col_graph2 = st.columns(2, gap="medium")
        
        with col_graph1:
            # Gráfico de barras agrupadas
            fig_grouped = go.Figure()
            
            x_pos = list(range(len(results_data["Escenario"])))
            width = 0.25
            
            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["AKI"],
                name="Lesión Renal Aguda",
                marker_color="#e74c3c",
                text=[f"{v:.1%}" for v in results_data["AKI"]],
                textposition="outside"
            ))
            
            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["RRT"],
                name="Terapia Reemplazo",
                marker_color="#f39c12",
                text=[f"{v:.1%}" for v in results_data["RRT"]],
                textposition="outside"
            ))
            
            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["Mortalidad"],
                name="Mortalidad",
                marker_color="#c0392b",
                text=[f"{v:.1%}" for v in results_data["Mortalidad"]],
                textposition="outside"
            ))
            
            fig_grouped.update_layout(
                title="Comparación de Riesgos por Escenario",
                xaxis_title="",
                yaxis_title="Probabilidad",
                barmode="group",
                hovermode="x unified",
                height=400,
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1])
            )
            
            st.plotly_chart(fig_grouped, use_container_width=True)
        
        with col_graph2:
            # Gráfico de líneas
            fig_lines = go.Figure()
            
            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["AKI"],
                name="AKI",
                mode="lines+markers",
                line=dict(color="#e74c3c", width=3),
                marker=dict(size=10),
                hovertemplate="<b>AKI</b><br>%{y:.2%}<extra></extra>"
            ))
            
            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["RRT"],
                name="RRT",
                mode="lines+markers",
                line=dict(color="#f39c12", width=3),
                marker=dict(size=10),
                hovertemplate="<b>RRT</b><br>%{y:.2%}<extra></extra>"
            ))
            
            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["Mortalidad"],
                name="Mortalidad",
                mode="lines+markers",
                line=dict(color="#c0392b", width=3),
                marker=dict(size=10),
                hovertemplate="<b>Mortalidad</b><br>%{y:.2%}<extra></extra>"
            ))
            
            fig_lines.update_layout(
                title="Evolución de Riesgos",
                xaxis_title="",
                yaxis_title="Probabilidad",
                hovermode="x unified",
                height=400,
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1])
            )
            
            st.plotly_chart(fig_lines, use_container_width=True)
        
        # Análisis de tendencias mejorado
        st.markdown("---")
        st.markdown("### 📌 Análisis de Tendencias y Patrones")
        
        # Calcular máximos y mínimos
        max_aki_idx = results_data["AKI"].index(max(results_data["AKI"]))
        min_aki_idx = results_data["AKI"].index(min(results_data["AKI"]))
        
        max_rrt_idx = results_data["RRT"].index(max(results_data["RRT"]))
        min_rrt_idx = results_data["RRT"].index(min(results_data["RRT"]))
        
        max_mort_idx = results_data["Mortalidad"].index(max(results_data["Mortalidad"]))
        min_mort_idx = results_data["Mortalidad"].index(min(results_data["Mortalidad"]))
        
        # Mostrar análisis
        col_an1, col_an2, col_an3 = st.columns(3, gap="medium")
        
        with col_an1:
            st.markdown("#### 🔴 Lesión Renal Aguda")
            st.error(f"Mayor: **{results_data['Escenario'][max_aki_idx]}**\n{results_data['AKI'][max_aki_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_aki_idx]}**\n{results_data['AKI'][min_aki_idx]:.2%}")
        
        with col_an2:
            st.markdown("#### 💧 Terapia Reemplazo")
            st.error(f"Mayor: **{results_data['Escenario'][max_rrt_idx]}**\n{results_data['RRT'][max_rrt_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_rrt_idx]}**\n{results_data['RRT'][min_rrt_idx]:.2%}")
        
        with col_an3:
            st.markdown("#### ⚠️ Mortalidad")
            st.error(f"Mayor: **{results_data['Escenario'][max_mort_idx]}**\n{results_data['Mortalidad'][max_mort_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_mort_idx]}**\n{results_data['Mortalidad'][min_mort_idx]:.2%}")
        
        # Análisis con IA si está configurado
        if is_openai_configured():
            st.markdown("---")
            st.markdown("### 🤖 Análisis Comparativo Mejorado con IA")
            
            with st.spinner("⏳ Generando análisis detallado..."):
                ai_comparative = generate_scenario_comparison(results_data["Escenario"], results_data)
                
                if ai_comparative:
                    st.markdown(ai_comparative)
                else:
                    st.error("❌ No se pudo generar el análisis con IA. Verifica tu API key.")
        else:
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                st.info("💡 Activa OpenAI para análisis más detallados")
            with col_ai2:
                st.caption("Lee SETUP.md para instrucciones")