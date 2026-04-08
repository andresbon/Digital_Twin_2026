import streamlit as st
import sys

# Inyectar la clase DigitalTwinBundle en __main__ para que joblib pueda encontrarla
from bundle_schema import DigitalTwinBundle
if hasattr(sys.modules["__main__"], "__dict__"):
    sys.modules["__main__"].DigitalTwinBundle = DigitalTwinBundle

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path

from risk_engine import predict_all_risks
from clinical_scenarios import get_all_scenarios, get_scenario_details
from config import is_openai_configured
from ai_interpreter import generate_clinical_interpretation, generate_scenario_comparison

from config import (
    DEFAULT_RANGES,
    HTN_MIN_SBP,
    HTN_MIN_DBP,
    HTN_MIN_MBP,
    DM_MIN_GLUCOSE,
    AUTHORS
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MARKOV_TRANSITIONS_PATH = DATA_DIR / "markov_dataset_clean.csv"
MARKOV_PANEL_PATH = DATA_DIR / "renal_markov_panel.csv"

def get_range_cfg(key, min_v, max_v, value_v, step_v):
    cfg = DEFAULT_RANGES.get(key, {}) if isinstance(DEFAULT_RANGES, dict) else {}
    return {
        "min": cfg.get("min", min_v),
        "max": cfg.get("max", max_v),
        "value": cfg.get("value", value_v),
        "step": cfg.get("step", step_v),
    }


def build_dynamic_ranges(has_htn: bool, has_dm: bool):
    ranges = {
        "creatinine": get_range_cfg("creatinine", 0.5, 5.0, 1.2, 0.1),
        "bun": get_range_cfg("bun", 5.0, 100.0, 20.0, 1.0),
        "sodium": get_range_cfg("sodium", 120.0, 160.0, 138.0, 1.0),
        "potassium": get_range_cfg("potassium", 2.5, 7.0, 4.0, 0.1),
        "hemoglobin": get_range_cfg("hemoglobin", 5.0, 18.0, 11.0, 0.1),
        "sbp_mean": get_range_cfg("sbp_mean", 80, 250, 120, 1),
        "dbp_mean": get_range_cfg("dbp_mean", 40, 150, 80, 1),
        "heart_rate_mean": get_range_cfg("heart_rate_mean", 30, 180, 80, 1),
        "chloride": get_range_cfg("chloride", 80.0, 130.0, 102.0, 1.0),
        "bicarbonate": get_range_cfg("bicarbonate", 5.0, 40.0, 24.0, 1.0),
        "glucose_lab": get_range_cfg("glucose_lab", 70.0, 500.0, 110.0, 1.0),
        "calcium": get_range_cfg("calcium", 5.0, 13.0, 9.0, 0.1),
        "hematocrit": get_range_cfg("hematocrit", 15.0, 60.0, 36.0, 0.1),
        "wbc": get_range_cfg("wbc", 0.5, 50.0, 8.0, 0.1),
        "platelet": get_range_cfg("platelet", 10.0, 1000.0, 250.0, 1.0),
        "resp_rate_mean": get_range_cfg("resp_rate_mean", 8, 40, 18, 1),
        "temperature_mean": get_range_cfg("temperature_mean", 34.0, 41.0, 36.8, 0.1),
        "spo2_mean": get_range_cfg("spo2_mean", 70, 100, 98, 1),
    }

    if has_htn:
        ranges["sbp_mean"]["min"] = max(ranges["sbp_mean"]["min"], HTN_MIN_SBP)
        ranges["dbp_mean"]["min"] = max(ranges["dbp_mean"]["min"], HTN_MIN_DBP)

        if ranges["sbp_mean"]["value"] < ranges["sbp_mean"]["min"]:
            ranges["sbp_mean"]["value"] = ranges["sbp_mean"]["min"]
        if ranges["dbp_mean"]["value"] < ranges["dbp_mean"]["min"]:
            ranges["dbp_mean"]["value"] = ranges["dbp_mean"]["min"]

    if has_dm:
        ranges["glucose_lab"]["min"] = max(float(ranges["glucose_lab"]["min"]), float(DM_MIN_GLUCOSE))
        if ranges["glucose_lab"]["value"] < ranges["glucose_lab"]["min"]:
            ranges["glucose_lab"]["value"] = ranges["glucose_lab"]["min"]

    return ranges


def clamp_state(key, min_value, max_value, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

    if st.session_state[key] < min_value:
        st.session_state[key] = min_value
    elif st.session_state[key] > max_value:
        st.session_state[key] = max_value


def sidebar_slider(label, key, cfg, fmt=None):
    use_float = any(isinstance(cfg[k], float) for k in ("min", "max", "value", "step"))

    if use_float:
        min_value = float(cfg["min"])
        max_value = float(cfg["max"])
        step_value = float(cfg["step"])
        default_value = float(max(min(cfg["value"], max_value), min_value))
    else:
        min_value = int(cfg["min"])
        max_value = int(cfg["max"])
        step_value = int(cfg["step"])
        default_value = int(max(min(cfg["value"], max_value), min_value))

    clamp_state(key, min_value, max_value, default_value)

    current_value = st.session_state[key]
    current_value = float(current_value) if use_float else int(current_value)

    kwargs = {
        "label": label,
        "min_value": min_value,
        "max_value": max_value,
        "value": current_value,
        "step": step_value,
        "key": key,
    }

    if fmt is not None:
        kwargs["format"] = fmt

    return st.sidebar.slider(**kwargs)


def get_risk_color(value):
    if value < 0.3:
        return "#2e7d5b"
    elif value < 0.7:
        return "#c28a16"
    else:
        return "#c25454"


def get_scenario_glossary():
    scenarios = get_all_scenarios()
    preferred_order = [
        "1. HTA Estable",
        "2. Diabetes Controlada",
        "3. Diabetes + HTA Moderada",
        "4. Diabetes + HTA con Riesgo Renal Aumentado",
        "5. Diabetes + HTA con Alto Riesgo de Eventos Renales"
    ]

    glossary = []
    for name in preferred_order:
        if name in scenarios:
            glossary.append((name, scenarios[name].get("description", "")))

    for name, data in scenarios.items():
        if name not in preferred_order:
            glossary.append((name, data.get("description", "")))

    return glossary

@st.dialog("Autores del proyecto", width="large")
def show_authors_dialog():
    st.markdown("### Equipo de desarrollo e investigación")
    st.write(
        "A continuación se presenta el perfil profesional de los autores del proyecto."
    )

    st.markdown(
        """
        <style>
        .author-name {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            color: #0f172a;
        }
        .author-role {
            font-size: 1rem;
            font-weight: 600;
            color: #2563eb;
            line-height: 1.5;
        }
        .author-profile {
            font-size: 0.98rem;
            line-height: 1.8;
            text-align: justify;
            color: #334155;
        }
        .author-divider {
            margin-top: 1rem;
            margin-bottom: 1rem;
            border-top: 1px solid #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for i, author in enumerate(AUTHORS):
        col1, col2, col3 = st.columns([1.1, 1.4, 3.2], gap="large", vertical_alignment="top")

        with col1:
            photo_path = Path(author["photo"])
            if photo_path.exists():
                st.image(str(photo_path), width=170)
            else:
                st.warning("Foto no disponible")

        with col2:
            st.markdown(f"<div class='author-name'>{author['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='author-role'>{author['role']}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"<div class='author-profile'>{author['profile']}</div>", unsafe_allow_html=True)

        if i < len(AUTHORS) - 1:
            st.markdown("<div class='author-divider'></div>", unsafe_allow_html=True)
    
@st.dialog("Guía de uso", width="large", dismissible=True, on_dismiss="ignore")
def open_instructions_dialog():
    tabs = st.tabs([
        "Vista general",
        "Predicción individual",
        "Análisis comparativo",
        "Interpretación",
        "Glosario",
        "Configuración técnica",
    ])

    with tabs[0]:
        st.markdown("""
### ¿Qué hace esta aplicación?

Este panel estima el riesgo de tres desenlaces clínicos:
- lesión renal aguda severa,
- necesidad de terapia de reemplazo renal,
- mortalidad intrahospitalaria.

La herramienta está pensada para análisis clínico y exploratorio de riesgo. No reemplaza el juicio médico.
""")
        st.info(
            "La aplicación se organiza en dos módulos: uno para evaluación individual del paciente "
            "y otro para comparación entre escenarios clínicos."
        )

    with tabs[1]:
        st.markdown("""
### ¿Cómo usar la pestaña individual?

Puedes trabajar de dos formas:

**Escenario predefinido**
- activa la opción correspondiente,
- selecciona el escenario,
- ejecuta la predicción.

**Ingreso manual**
- define género y edad,
- selecciona hipertensión, diabetes o ambas,
- ajusta los parámetros disponibles,
- ejecuta la predicción.
""")
        st.markdown("""
### Reglas de coherencia clínica

- Si seleccionas hipertensión, la presión arterial no podrá bajar a rangos incoherentes para ese perfil.
- Si seleccionas diabetes, la glucosa se restringe a rangos coherentes con ese historial.
- Si no seleccionas hipertensión ni diabetes, la predicción manual no se habilita.
""")

    with tabs[2]:
        st.markdown("""
### ¿Cómo usar la pestaña comparativa?

Esta sección permite comparar varios escenarios clínicos al mismo tiempo.

**Pasos**
- selecciona uno o más escenarios,
- haz clic en analizar,
- revisa la tabla y los gráficos comparativos.

**Utilidad**
- comparar perfiles de riesgo,
- observar cambios relativos entre escenarios,
- identificar cuál perfil concentra mayor vulnerabilidad.
""")

    with tabs[3]:
        st.markdown("""
### Interpretación general de resultados

La aplicación presenta tres probabilidades:
- lesión renal aguda severa,
- terapia de reemplazo renal,
- mortalidad.

### Lectura general
- **Bajo:** menor a 0.30
- **Moderado:** entre 0.30 y 0.69
- **Alto:** 0.70 o más

Estas salidas deben interpretarse como apoyo analítico del modelo y no como una decisión clínica automática.
""")

    with tabs[4]:
        st.markdown("### Escenarios predefinidos")
        for name, description in get_scenario_glossary():
            st.markdown(f"**{name}**")
            st.write(description)

    with tabs[5]:
        if not is_openai_configured():
            st.markdown("""
### Configuración técnica opcional

El análisis complementario con IA es opcional.

Si deseas activarlo:
1. obtén tu API key,
2. crea un archivo `.env` en la raíz del proyecto,
3. agrega `OPENAI_API_KEY`,
4. reinicia la aplicación.

También puedes revisar `SETUP.md`.
""")
        else:
            st.success("La integración complementaria con IA está configurada correctamente.")


RENAL_STATES = [
    "stable",
    "ckd_no_aki",
    "aki_stage1",
    "aki_severe",
    "rrt",
    "death"
]

STATE_LABELS = {
    "stable": "Estable",
    "ckd_no_aki": "ERC sin lesión aguda",
    "aki_stage1": "Lesión renal aguda estadio 1",
    "aki_severe": "Lesión renal aguda severa",
    "rrt": "Terapia de reemplazo renal",
    "death": "Fallecimiento"
}

KIDNEY_IMAGES = {
    "stable": "images/kidney_stable.png",
    "ckd_no_aki": "images/kidney_ckd_no_aki.png",
    "aki_stage1": "images/kidney_aki_stage1.png",
    "aki_severe": "images/kidney_aki_severe.png",
    "rrt": "images/kidney_rrt.png",
    "death": "images/kidney_death.png",
}


def normalize_row(row):
    row = np.clip(row, 0, None)
    total = row.sum()

    if total <= 0:
        row = np.zeros_like(row)
        row[-1] = 1.0
        return row

    row = row / total

    diff = 1.0 - row.sum()
    row[np.argmax(row)] += diff

    return row

def simulate_markov_path(initial_state_idx, transition_matrix, steps=12, seed=None):
    rng = np.random.default_rng(seed)
    states = [initial_state_idx]

    for _ in range(steps):
        current = states[-1]

        probs = normalize_row(transition_matrix[current].copy())

        next_state = rng.choice(len(RENAL_STATES), p=probs)
        states.append(int(next_state))

    return states


def simulate_markov_cohort(initial_state_idx, transition_matrix, steps=12, n_simulations=500, seed=42):
    rng = np.random.default_rng(seed)
    all_paths = []

    for _ in range(n_simulations):
        states = [initial_state_idx]
        for _ in range(steps):
            current = states[-1]
            probs = normalize_row(transition_matrix[current].copy())
            next_state = rng.choice(len(RENAL_STATES), p=probs)
            states.append(int(next_state))
        all_paths.append(states)

    return np.array(all_paths)


def build_probability_evolution(all_paths):
    """
    Devuelve probabilidad por estado en cada punto temporal.
    """
    n_simulations, n_times = all_paths.shape
    records = []

    for t in range(n_times):
        counts = np.bincount(all_paths[:, t], minlength=len(RENAL_STATES))
        probs = counts / n_simulations

        row = {"Tiempo": t}
        for i, state in enumerate(RENAL_STATES):
            row[state] = probs[i]
        records.append(row)

    return pd.DataFrame(records)


def build_most_likely_trajectory(prob_df):
    most_likely_states = []
    for _, row in prob_df.iterrows():
        probs = [row[state] for state in RENAL_STATES]
        most_likely_states.append(RENAL_STATES[int(np.argmax(probs))])

    return pd.DataFrame({
        "Tiempo": prob_df["Tiempo"],
        "Estado más probable": most_likely_states
    })


def get_time_labels(horizon_choice, steps):
    if horizon_choice == "6 meses":
        return [f"Mes {i}" for i in range(steps + 1)]
    elif horizon_choice == "12 meses":
        return [f"Mes {i}" for i in range(steps + 1)]
    elif horizon_choice == "24 meses":
        return [f"Mes {i}" for i in range(steps + 1)]
    elif horizon_choice == "3 años":
        return [f"Año {i/12:.1f}" if i > 0 else "Inicio" for i in range(steps + 1)]
    return [str(i) for i in range(steps + 1)]

def apply_treatment_effects(transition_matrix, patient_data, treatment_plan):
    """
    Ajusta la matriz si el paciente recibe intervención.
    treatment_plan:
        {
            "bp_control": bool,
            "glucose_control": bool,
            "renal_protection": bool,
            "effect_strength": float entre 0 y 1
        }
    """
    matrix = transition_matrix.copy()
    strength = float(treatment_plan.get("effect_strength", 0.5))

    has_htn = patient_data.get("hypertension_flag", 0) == 1
    has_dm = patient_data.get("diabetes_flag", 0) == 1
    has_ckd = patient_data.get("ckd_flag", 0) == 1

    bp_control = treatment_plan.get("bp_control", False)
    glucose_control = treatment_plan.get("glucose_control", False)
    renal_protection = treatment_plan.get("renal_protection", False)

    total_improvement = 0.0

    if has_htn and bp_control:
        total_improvement += 0.04 * strength

    if has_dm and glucose_control:
        total_improvement += 0.05 * strength

    if renal_protection:
        total_improvement += 0.06 * strength

    if has_ckd:
        total_improvement *= 0.85

    # Mejorar estados 1, 2 y 3
    for i in [1, 2, 3]:
        shift = min(matrix[i, i + 1] * 0.5 if i < 4 else 0, total_improvement)

        if i < 4:
            matrix[i, i + 1] -= shift
            matrix[i, i] += shift * 0.65

            if i - 1 >= 0:
                backward_bonus = shift * 0.35
                matrix[i, i - 1] += backward_bonus
                matrix[i, i] -= backward_bonus * 0.15

    # En estados más tempranos, aumentar permanencia si el tratamiento ayuda
    if total_improvement > 0:
        matrix[0, 0] += min(0.05 * strength, 0.03)
        matrix[0, 1] -= min(matrix[0, 1] * 0.25, 0.03)

    # Normalizar
    for i in range(matrix.shape[0]):
        matrix[i] = normalize_row(matrix[i])

    return matrix

@st.cache_data
def load_markov_transitions():
    df = pd.read_csv(MARKOV_TRANSITIONS_PATH)
    return df


@st.cache_data
def load_markov_panel():
    df = pd.read_csv(MARKOV_PANEL_PATH)
    return df


def build_transition_matrix_from_csv():
    df = load_markov_transitions().copy()

    # Orden fijo de estados según tu query
    markov_states = ["stable", "ckd_no_aki", "aki_stage1", "aki_severe", "rrt", "death"]

    matrix_df = (
        df.pivot(index="state_from", columns="state_to", values="transition_prob")
          .reindex(index=markov_states, columns=markov_states, fill_value=0.0)
          .fillna(0.0)
    )

    matrix = matrix_df.to_numpy(dtype=float)

    # Normalizar por seguridad
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    matrix = matrix / row_sums

    return markov_states, matrix, matrix_df

def get_initial_markov_state_from_patient(patient_data, risks):
    aki = risks.get("aki_severe", {}).get("probability", 0)
    rrt = risks.get("rrt_needed", {}).get("probability", 0)
    mortality = risks.get("in_hospital_mortality", {}).get("probability", 0)

    ckd_flag = int(patient_data.get("ckd_flag", 0))
    creatinine = float(patient_data.get("creatinine", 1.0))
    bun = float(patient_data.get("bun", 20.0))

    if mortality >= 0.95:
        return "death"
    if rrt >= 0.50:
        return "rrt"
    if aki >= 0.60 or creatinine >= 2.5:
        return "aki_severe"
    if aki >= 0.25 or creatinine >= 1.5 or bun >= 30:
        return "aki_stage1"
    if ckd_flag == 1:
        return "ckd_no_aki"
    return "stable"

st.set_page_config(
    layout="wide",
    page_title="Monitor de Riesgo Renal",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "Monitor Digital Twin para Predicción de Riesgos Renales v1.0",
    },
)

st.markdown("""
<style>
    :root {
        --primary-color: #0f4c81;
        --primary-2: #1e88e5;
        --secondary-color: #1f2937;
        --bg-soft: #f4f8fb;
        --card-bg: #ffffff;
        --border-soft: #d8e3ee;
        --text-main: #1b2a3a;
        --text-soft: #5f7285;
        --success-color: #2e7d5b;
        --warning-color: #c28a16;
        --danger-color: #c25454;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", Arial, sans-serif;
        color: var(--text-main);
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: var(--text-main);
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.25rem;
        border-bottom: none !important;
        padding-bottom: 0 !important;
    }

    h2 {
        color: var(--primary-color);
        font-weight: 700;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }

    h3 {
        color: var(--secondary-color);
        font-weight: 650;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #eef4f8 100%);
        border-right: 1px solid var(--border-soft);
    }

    [data-testid="metric-container"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
        border: 1px solid var(--border-soft);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(15, 76, 129, 0.08);
    }

    .hero-shell {
        background: linear-gradient(135deg, #f8fbff 0%, #eef5fb 100%);
        border: 1px solid var(--border-soft);
        border-radius: 22px;
        padding: 28px 30px 20px 30px;
        box-shadow: 0 10px 28px rgba(15, 76, 129, 0.08);
        margin-bottom: 18px;
    }

    .hero-subtitle {
        color: var(--text-soft);
        font-size: 1.02rem;
        margin-top: 0.2rem;
        margin-bottom: 0.15rem;
    }

    .hero-divider {
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--primary-2));
        border-radius: 999px;
        margin-top: 14px;
    }

    .action-caption {
        color: var(--text-soft);
        font-size: 0.95rem;
        margin-bottom: 0.55rem;
        font-weight: 600;
    }

    .stButton > button {
        border-radius: 12px;
        padding: 0.78rem 1rem;
        font-weight: 650;
        border: 1px solid #d7e4ef;
        width: 100%;
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(15, 76, 129, 0.06);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(15, 76, 129, 0.12);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #f2f6fa;
        border-radius: 10px 10px 0 0;
        padding: 10px 16px;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary-color) !important;
        border-bottom: 2px solid var(--primary-color) !important;
        background: white !important;
    }

    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 14px;
        border-left-width: 4px !important;
        padding: 14px 16px;
    }

    .stInfo {
        background: rgba(30, 136, 229, 0.08);
        border-left-color: var(--primary-2) !important;
    }

    .stSuccess {
        background: rgba(46, 125, 91, 0.08);
        border-left-color: var(--success-color) !important;
    }

    .stWarning {
        background: rgba(194, 138, 22, 0.10);
        border-left-color: var(--warning-color) !important;
    }

    .stError {
        background: rgba(194, 84, 84, 0.08);
        border-left-color: var(--danger-color) !important;
    }

    .empty-state {
        background: linear-gradient(180deg, #f8fbff 0%, #eef5fb 100%);
        border: 1px dashed #bfd2e4;
        border-radius: 18px;
        padding: 26px;
        color: var(--text-main);
        margin-top: 14px;
    }

    .section-card {
        background: white;
        border: 1px solid var(--border-soft);
        border-radius: 18px;
        padding: 8px 14px 18px 14px;
        box-shadow: 0 6px 18px rgba(15, 76, 129, 0.05);
    }
</style>
""", unsafe_allow_html=True)

if "show_predictions" not in st.session_state:
    st.session_state.show_predictions = False

# Sidebar
st.sidebar.markdown("### Configuración de la aplicación")
st.sidebar.header("Datos clínicos del paciente")

use_scenario = st.sidebar.checkbox("Usar escenario predefinido", value=False)

hypertension = False
diabetes = False
patient_data = {}

if use_scenario:
    scenario_name = st.sidebar.selectbox(
        "Selecciona un escenario",
        list(get_all_scenarios().keys())
    )
    patient_data = get_scenario_details(scenario_name)
    st.sidebar.info(f"Descripción: {get_all_scenarios()[scenario_name]['description']}")

    hypertension = patient_data.get("hypertension_flag", 0) == 1
    diabetes = patient_data.get("diabetes_flag", 0) == 1

else:
    st.sidebar.subheader("Información demográfica")
    gender = st.sidebar.selectbox("Género", ["Masculino", "Femenino"])
    age = st.sidebar.slider("Edad", 18, 100, 60)

    st.sidebar.subheader("Historial médico")
    hypertension = st.sidebar.checkbox("Hipertensión", value=False, key="manual_hypertension")
    diabetes = st.sidebar.checkbox("Diabetes", value=False, key="manual_diabetes")

    history_selected = hypertension or diabetes
    dynamic_ranges = build_dynamic_ranges(hypertension, diabetes)

    creatinine = dynamic_ranges["creatinine"]["value"]
    bun = dynamic_ranges["bun"]["value"]
    sodium = dynamic_ranges["sodium"]["value"]
    potassium = dynamic_ranges["potassium"]["value"]
    hemoglobin = dynamic_ranges["hemoglobin"]["value"]

    sbp = dynamic_ranges["sbp_mean"]["value"]
    dbp = dynamic_ranges["dbp_mean"]["value"]
    heart_rate = dynamic_ranges["heart_rate_mean"]["value"]

    chloride = dynamic_ranges["chloride"]["value"]
    bicarbonate = dynamic_ranges["bicarbonate"]["value"]
    glucose_lab = dynamic_ranges["glucose_lab"]["value"]
    calcium = dynamic_ranges["calcium"]["value"]
    hematocrit = dynamic_ranges["hematocrit"]["value"]
    wbc = dynamic_ranges["wbc"]["value"]
    platelet = dynamic_ranges["platelet"]["value"]

    resp_rate = dynamic_ranges["resp_rate_mean"]["value"]
    temperature = dynamic_ranges["temperature_mean"]["value"]
    spo2 = dynamic_ranges["spo2_mean"]["value"]

    if not history_selected:
        st.sidebar.warning(
            "Selecciona hipertensión, diabetes o ambas para habilitar "
            "los parámetros clínicos."
        )
        st.session_state.show_predictions = False
    else:
        if hypertension and diabetes:
            st.sidebar.info(
                "Perfil activo: hipertensión y diabetes. "
                "Se aplican restricciones coherentes para presión arterial y glucosa."
            )
        elif hypertension:
            st.sidebar.info(
                "Perfil activo: hipertensión. "
                "La presión arterial se ajusta a rangos coherentes con este historial."
            )
        elif diabetes:
            st.sidebar.info(
                "Perfil activo: diabetes. "
                "La glucosa se ajusta a rangos coherentes con este historial."
            )

        st.sidebar.subheader("Parámetros laborales")
        creatinine = sidebar_slider("Creatinina (mg/dL)", "creatinine", dynamic_ranges["creatinine"], "%.2f")
        bun = sidebar_slider("BUN (mg/dL)", "bun", dynamic_ranges["bun"], "%.0f")
        sodium = sidebar_slider("Sodio (mEq/L)", "sodium", dynamic_ranges["sodium"], "%.0f")
        potassium = sidebar_slider("Potasio (mEq/L)", "potassium", dynamic_ranges["potassium"], "%.2f")
        hemoglobin = sidebar_slider("Hemoglobina (g/dL)", "hemoglobin", dynamic_ranges["hemoglobin"], "%.2f")

        st.sidebar.subheader("Signos vitales")
        sbp = sidebar_slider("Presión arterial sistólica (mmHg)", "sbp_mean", dynamic_ranges["sbp_mean"], "%.0f")
        dbp = sidebar_slider("Presión arterial diastólica (mmHg)", "dbp_mean", dynamic_ranges["dbp_mean"], "%.0f")
        heart_rate = sidebar_slider("Frecuencia cardíaca (bpm)", "heart_rate_mean", dynamic_ranges["heart_rate_mean"], "%.0f")

        st.sidebar.subheader("Laboratorios adicionales")
        chloride = sidebar_slider("Cloro (mEq/L)", "chloride", dynamic_ranges["chloride"], "%.0f")
        bicarbonate = sidebar_slider("Bicarbonato (mEq/L)", "bicarbonate", dynamic_ranges["bicarbonate"], "%.0f")
        glucose_lab = sidebar_slider("Glucosa (mg/dL)", "glucose_lab", dynamic_ranges["glucose_lab"], "%.0f")
        calcium = sidebar_slider("Calcio (mg/dL)", "calcium", dynamic_ranges["calcium"], "%.1f")
        hematocrit = sidebar_slider("Hematocrito (%)", "hematocrit", dynamic_ranges["hematocrit"], "%.1f")
        wbc = sidebar_slider("Leucocitos (K/uL)", "wbc", dynamic_ranges["wbc"], "%.1f")
        platelet = sidebar_slider("Plaquetas (K/uL)", "platelet", dynamic_ranges["platelet"], "%.0f")

        st.sidebar.subheader("Signos vitales adicionales")
        resp_rate = sidebar_slider("Frecuencia respiratoria (rpm)", "resp_rate_mean", dynamic_ranges["resp_rate_mean"], "%.0f")
        temperature = sidebar_slider("Temperatura (°C)", "temperature_mean", dynamic_ranges["temperature_mean"], "%.1f")
        spo2 = sidebar_slider("SpO2 (%)", "spo2_mean", dynamic_ranges["spo2_mean"], "%.0f")

    mbp = (sbp + 2 * dbp) / 3

    if hypertension and mbp < HTN_MIN_MBP:
        st.sidebar.error(
            f"La presión arterial media calculada ({mbp:.1f}) sigue siendo baja "
            f"para un perfil hipertenso. Ajusta PAS y PAD."
        )

    patient_data = {
        "gender": 1 if gender == "Masculino" else 0,
        "age": age,
        "hypertension_flag": 1 if hypertension else 0,
        "diabetes_flag": 1 if diabetes else 0,
        "ckd_flag": 0,
        "creatinine": float(creatinine),
        "bun": float(bun),
        "sodium": float(sodium),
        "potassium": float(potassium),
        "hemoglobin": float(hemoglobin),
        "sbp_mean": float(sbp),
        "dbp_mean": float(dbp),
        "heart_rate_mean": float(heart_rate),
        "chloride": float(chloride),
        "bicarbonate": float(bicarbonate),
        "glucose_lab": float(glucose_lab),
        "calcium": float(calcium),
        "hematocrit": float(hematocrit),
        "wbc": float(wbc),
        "platelet": float(platelet),
        "mbp_mean": float(mbp),
        "resp_rate_mean": float(resp_rate),
        "temperature_mean": float(temperature),
        "spo2_mean": float(spo2),
    }

with st.sidebar.expander("Información técnica", expanded=False):
    if is_openai_configured():
        st.write("La integración complementaria con IA está configurada.")
    else:
        st.write("La integración complementaria con IA no está configurada.")
        st.write("Puedes activarla desde el archivo SETUP.md.")

can_predict = use_scenario or (hypertension or diabetes)

# Encabezado principal
st.markdown("""
<div class="hero-shell">
    <h1>Panel de Control Digital Twin</h1>
    <h2>Monitor de Riesgo Renal</h2>
    <div class="hero-subtitle">
        Plataforma de apoyo analítico para evaluación individual y comparativa de riesgo renal.
    </div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="action-caption">Acciones principales</div>', unsafe_allow_html=True)
action_col1, action_col2, action_col3 = st.columns([1.75, 1.15, 1.15])

with action_col1:
    if st.button(
        "Predecir condición del paciente",
        key="predict_top_btn",
        use_container_width=True,
        disabled=not can_predict,
    ):
        st.session_state.show_predictions = True

with action_col2:
    if st.button("Instrucciones", key="open_instructions_btn", use_container_width=True):
        open_instructions_dialog()

with action_col3:
    if  st.button("Autores",use_container_width=True):
        show_authors_dialog()
# Predicción
validation_message = None
runtime_error = None
risks = None

if st.session_state.show_predictions:
    if not use_scenario and not can_predict:
        validation_message = "Debes seleccionar hipertensión, diabetes o ambas antes de predecir."
    elif diabetes and patient_data.get("glucose_lab", 0) < DM_MIN_GLUCOSE:
        validation_message = "La glucosa no es coherente con el historial de diabetes."
    elif hypertension and patient_data.get("sbp_mean", 0) < HTN_MIN_SBP:
        validation_message = "La presión sistólica no es coherente con el historial de hipertensión."
    elif hypertension and patient_data.get("dbp_mean", 0) < HTN_MIN_DBP:
        validation_message = "La presión diastólica no es coherente con el historial de hipertensión."
    elif hypertension and patient_data.get("mbp_mean", 0) < HTN_MIN_MBP:
        validation_message = "La presión arterial media no es coherente con el historial de hipertensión."
    else:
        try:
            risks = predict_all_risks(patient_data)
        except Exception as e:
            runtime_error = str(e)

tab1, tab2, tab3 = st.tabs([
    "Predicción individual",
    "Análisis comparativo",
    "Evolución temporal"
])

with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    if validation_message:
        st.warning(validation_message)

    elif runtime_error:
        st.error(f"Error al generar las predicciones: {runtime_error}")

    elif risks is not None:
        aki = risks.get("aki_severe", {}).get("probability", 0)
        rrt = risks.get("rrt_needed", {}).get("probability", 0)
        mortality = risks.get("in_hospital_mortality", {}).get("probability", 0)

        st.markdown("## Resultados de la predicción")

        col1, col2, col3 = st.columns(3, gap="medium")

        with col1:
            st.metric("Lesión renal aguda", f"{aki:.2%}")
            if aki < 0.3:
                st.caption("Riesgo bajo")
            elif aki < 0.7:
                st.caption("Riesgo moderado")
            else:
                st.caption("Riesgo alto")

        with col2:
            st.metric("Terapia de reemplazo renal", f"{rrt:.2%}")
            if rrt < 0.3:
                st.caption("Probabilidad baja")
            elif rrt < 0.7:
                st.caption("Probabilidad moderada")
            else:
                st.caption("Probabilidad alta")

        with col3:
            st.metric("Mortalidad", f"{mortality:.2%}")
            if mortality < 0.3:
                st.caption("Riesgo bajo")
            elif mortality < 0.7:
                st.caption("Riesgo moderado")
            else:
                st.caption("Riesgo alto")

        st.markdown("### Distribución comparativa de riesgos")
        col_graph1, col_graph2 = st.columns(2)

        with col_graph1:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=["AKI", "RRT", "Mortalidad"],
                y=[aki, rrt, mortality],
                marker=dict(
                    color=[get_risk_color(aki), get_risk_color(rrt), get_risk_color(mortality)],
                    line=dict(color="white", width=2),
                ),
                text=[f"{aki:.1%}", f"{rrt:.1%}", f"{mortality:.1%}"],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Riesgo: %{y:.2%}<extra></extra>",
            ))
            fig_bar.update_layout(
                title="Riesgos por tipo",
                xaxis_title="",
                yaxis_title="Probabilidad",
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1]),
                height=400,
                hovermode="x unified",
                showlegend=False,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_graph2:
            fig_gauge = go.Figure()
            avg_risk = (aki + rrt + mortality) / 3

            fig_gauge.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=avg_risk * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Riesgo promedio"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": get_risk_color(avg_risk)},
                    "steps": [
                        {"range": [0, 30], "color": "rgba(46, 125, 91, 0.18)"},
                        {"range": [30, 70], "color": "rgba(194, 138, 22, 0.18)"},
                        {"range": [70, 100], "color": "rgba(194, 84, 84, 0.18)"},
                    ],
                    "threshold": {
                        "line": {"color": "#9b1c1c", "width": 2},
                        "thickness": 0.75,
                        "value": 70,
                    },
                },
            ))
            fig_gauge.update_layout(height=400, font=dict(size=12))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("### Interpretación clínica")
        col_inter1, col_inter2, col_inter3 = st.columns(3, gap="medium")

        with col_inter1:
            st.markdown("#### Lesión renal aguda")
            if aki < 0.3:
                st.success("Riesgo bajo.\n\nProbabilidad baja de desarrollar AKI severa.")
            elif aki < 0.7:
                st.warning("Riesgo moderado.\n\nSe recomienda monitoreo de función renal.")
            else:
                st.error("Riesgo alto.\n\nSe requiere vigilancia e intervención oportuna.")

        with col_inter2:
            st.markdown("#### Terapia de reemplazo renal")
            if rrt < 0.3:
                st.success("Probabilidad baja.\n\nNo se sugiere necesidad inmediata de reemplazo renal.")
            elif rrt < 0.7:
                st.warning("Probabilidad moderada.\n\nConviene seguimiento estrecho de la función renal.")
            else:
                st.error("Probabilidad alta.\n\nDebe considerarse preparación para soporte renal.")

        with col_inter3:
            st.markdown("#### Mortalidad")
            if mortality < 0.3:
                st.success("Riesgo bajo.\n\nEl pronóstico general es más favorable.")
            elif mortality < 0.7:
                st.warning("Riesgo moderado.\n\nSe recomienda monitoreo intensivo.")
            else:
                st.error("Riesgo alto.\n\nSe requiere especial vigilancia clínica.")

        st.markdown("### Recomendaciones de seguimiento")
        rec_cols = st.columns(2, gap="medium")

        with rec_cols[0]:
            st.markdown("#### Monitoreo recomendado")
            recommendations = []

            if aki > 0.5:
                recommendations.append("Monitoreo diario de creatinina y BUN.")
            if rrt > 0.5:
                recommendations.append("Valorar seguimiento por nefrología.")
            if mortality > 0.5:
                recommendations.append("Considerar vigilancia clínica intensiva.")
            if diabetes:
                recommendations.append("Optimizar control glucémico.")
            if hypertension:
                recommendations.append("Optimizar control de presión arterial.")

            if recommendations:
                for rec in recommendations:
                    st.write(f"- {rec}")
            else:
                st.success("Se recomienda seguimiento rutinario.")

        with rec_cols[1]:
            st.markdown("#### Información general al paciente")
            st.info("""
                Mantener hidratación adecuada, seguir la dieta indicada, tomar la medicación según prescripción
                y reportar oportunamente síntomas como fatiga, edema o disminución del estado general.
                """)

        if is_openai_configured():
            with st.spinner("Generando análisis clínico complementario..."):
                ai_interpretation = generate_clinical_interpretation(patient_data, risks)
                if ai_interpretation:
                    st.markdown(ai_interpretation)
                else:
                    st.error("No se pudo generar el análisis complementario con IA.")
        else:
            st.info("El análisis complementario con IA no está activado. La predicción principal sigue disponible.")

    else:
        st.markdown("""
        <div class="empty-state">
            <h3>Listo para comenzar</h3>
            <p>
                Ajusta los parámetros clínicos en la barra lateral o selecciona un escenario predefinido.
                Luego usa el botón <strong>Predecir condición del paciente</strong> para generar los resultados.
            </p>
            <p>
                Si deseas conocer la estructura de la herramienta, abre <strong>Instrucciones</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("# Análisis comparativo de escenarios")
    st.markdown("""
        Compara los perfiles de riesgo entre diferentes escenarios clínicos para entender cómo
        las comorbilidades cardiometabólicas y los parámetros iniciales afectan los resultados clínicos.
        """)

    all_scenarios = list(get_all_scenarios().keys())

    col_select1, col_select2 = st.columns([3, 1])
    with col_select1:
        selected_scenarios = st.multiselect(
            "Selecciona escenarios para comparar:",
            all_scenarios,
            default=all_scenarios if len(all_scenarios) <= 4 else all_scenarios[:4],
        )
    with col_select2:
        st.markdown("")
        st.markdown("")
        execute_analysis = st.button("Analizar", use_container_width=True, key="comparative_btn")

    if execute_analysis and selected_scenarios:
        results_data = {
            "Escenario": [],
            "AKI": [],
            "RRT": [],
            "Mortalidad": [],
        }

        with st.spinner("Calculando predicciones para los escenarios seleccionados..."):
            for scenario_name in selected_scenarios:
                scenario_data = get_scenario_details(scenario_name)
                scenario_risks = predict_all_risks(scenario_data)

                scenario_label = scenario_name.split(". ", 1)[1] if ". " in scenario_name else scenario_name
                results_data["Escenario"].append(scenario_label)
                results_data["AKI"].append(scenario_risks.get("aki_severe", {}).get("probability", 0))
                results_data["RRT"].append(scenario_risks.get("rrt_needed", {}).get("probability", 0))
                results_data["Mortalidad"].append(scenario_risks.get("in_hospital_mortality", {}).get("probability", 0))

        df_results = pd.DataFrame(results_data)

        st.markdown("## Resultados del análisis")
        st.markdown("### Tabla comparativa de riesgos")

        st.dataframe(
            df_results.style.format({
                "AKI": "{:.2%}",
                "RRT": "{:.2%}",
                "Mortalidad": "{:.2%}",
            }).background_gradient(
                subset=["AKI", "RRT", "Mortalidad"],
                cmap="RdYlGn_r",
                vmin=0,
                vmax=1,
            ),
            use_container_width=True,
            height=300,
        )

        st.markdown("### Visualización de riesgos")
        col_graph1, col_graph2 = st.columns(2, gap="medium")

        with col_graph1:
            fig_grouped = go.Figure()

            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["AKI"],
                name="Lesión renal aguda",
                marker_color="#c25454",
                text=[f"{v:.1%}" for v in results_data["AKI"]],
                textposition="outside",
            ))

            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["RRT"],
                name="Terapia de reemplazo renal",
                marker_color="#c28a16",
                text=[f"{v:.1%}" for v in results_data["RRT"]],
                textposition="outside",
            ))

            fig_grouped.add_trace(go.Bar(
                x=results_data["Escenario"],
                y=results_data["Mortalidad"],
                name="Mortalidad",
                marker_color="#8b2f3d",
                text=[f"{v:.1%}" for v in results_data["Mortalidad"]],
                textposition="outside",
            ))

            fig_grouped.update_layout(
                title="Comparación de riesgos por escenario",
                xaxis_title="",
                yaxis_title="Probabilidad",
                barmode="group",
                hovermode="x unified",
                height=400,
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1]),
            )

            st.plotly_chart(fig_grouped, use_container_width=True)

        with col_graph2:
            fig_lines = go.Figure()

            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["AKI"],
                name="AKI",
                mode="lines+markers",
                line=dict(color="#c25454", width=3),
                marker=dict(size=10),
                hovertemplate="<b>AKI</b><br>%{y:.2%}<extra></extra>",
            ))

            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["RRT"],
                name="RRT",
                mode="lines+markers",
                line=dict(color="#c28a16", width=3),
                marker=dict(size=10),
                hovertemplate="<b>RRT</b><br>%{y:.2%}<extra></extra>",
            ))

            fig_lines.add_trace(go.Scatter(
                x=results_data["Escenario"],
                y=results_data["Mortalidad"],
                name="Mortalidad",
                mode="lines+markers",
                line=dict(color="#8b2f3d", width=3),
                marker=dict(size=10),
                hovertemplate="<b>Mortalidad</b><br>%{y:.2%}<extra></extra>",
            ))

            fig_lines.update_layout(
                title="Evolución de riesgos",
                xaxis_title="",
                yaxis_title="Probabilidad",
                hovermode="x unified",
                height=400,
                plot_bgcolor="rgba(240,240,240,0.3)",
                yaxis=dict(range=[0, 1]),
            )

            st.plotly_chart(fig_lines, use_container_width=True)

        st.markdown("### Análisis de tendencias y patrones")

        max_aki_idx = results_data["AKI"].index(max(results_data["AKI"]))
        min_aki_idx = results_data["AKI"].index(min(results_data["AKI"]))

        max_rrt_idx = results_data["RRT"].index(max(results_data["RRT"]))
        min_rrt_idx = results_data["RRT"].index(min(results_data["RRT"]))

        max_mort_idx = results_data["Mortalidad"].index(max(results_data["Mortalidad"]))
        min_mort_idx = results_data["Mortalidad"].index(min(results_data["Mortalidad"]))

        col_an1, col_an2, col_an3 = st.columns(3, gap="medium")

        with col_an1:
            st.markdown("#### Lesión renal aguda")
            st.error(f"Mayor: **{results_data['Escenario'][max_aki_idx]}**\n{results_data['AKI'][max_aki_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_aki_idx]}**\n{results_data['AKI'][min_aki_idx]:.2%}")

        with col_an2:
            st.markdown("#### Terapia de reemplazo renal")
            st.error(f"Mayor: **{results_data['Escenario'][max_rrt_idx]}**\n{results_data['RRT'][max_rrt_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_rrt_idx]}**\n{results_data['RRT'][min_rrt_idx]:.2%}")

        with col_an3:
            st.markdown("#### Mortalidad")
            st.error(f"Mayor: **{results_data['Escenario'][max_mort_idx]}**\n{results_data['Mortalidad'][max_mort_idx]:.2%}")
            st.success(f"Menor: **{results_data['Escenario'][min_mort_idx]}**\n{results_data['Mortalidad'][min_mort_idx]:.2%}")

        if is_openai_configured():
            st.markdown("### Análisis comparativo mejorado con IA")
            with st.spinner("Generando análisis comparativo..."):
                ai_comparative = generate_scenario_comparison(results_data["Escenario"], results_data)
                if ai_comparative:
                    st.markdown(ai_comparative)
                else:
                    st.error("No se pudo generar el análisis comparativo con IA.")
        else:
            st.info("El análisis comparativo principal está disponible. La capa complementaria con IA no está activada.")

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown("# Evolución temporal del paciente")
    st.markdown("""
Esta sección simula la trayectoria renal mensual del paciente usando la matriz de transición
estimada desde el panel longitudinal Markov. Se comparan dos escenarios:
**sin intervención** y **con intervención terapéutica**.
""")

    if not can_predict:
        st.info("Primero selecciona un escenario predefinido o configura un paciente con diabetes y/o hipertensión.")
    else:
        temporal_col1, temporal_col2, temporal_col3 = st.columns([1.2, 1.1, 1.1])

        with temporal_col1:
            horizon_choice = st.selectbox(
                "Horizonte de simulación",
                ["6 meses", "12 meses", "24 meses", "3 años"],
                index=1,
                key="temporal_horizon"
            )

        with temporal_col2:
            n_simulations = st.slider(
                "Número de simulaciones",
                min_value=100,
                max_value=2000,
                value=500,
                step=100,
                key="temporal_nsim"
            )

        with temporal_col3:
            seed_value = st.number_input(
                "Semilla",
                min_value=0,
                max_value=99999,
                value=42,
                step=1,
                key="temporal_seed"
            )

        st.markdown("## Configuración de intervención")
        int_col1, int_col2, int_col3, int_col4 = st.columns(4)

        with int_col1:
            bp_control = st.checkbox("Control de presión arterial", value=True, key="tx_bp")
        with int_col2:
            glucose_control = st.checkbox("Control glucémico", value=True, key="tx_glucose")
        with int_col3:
            renal_protection = st.checkbox("Protección renal", value=True, key="tx_renal")
        with int_col4:
            effect_strength = st.slider(
                "Intensidad del tratamiento",
                min_value=0.1,
                max_value=1.0,
                value=0.6,
                step=0.1,
                key="tx_strength"
            )

        horizon_map = {
            "6 meses": 6,
            "12 meses": 12,
            "24 meses": 24,
            "3 años": 36,
        }
        steps = horizon_map[horizon_choice]

        simulate_btn = st.button("Simular evolución temporal", key="simulate_temporal_btn")

        if simulate_btn:
            local_risks = risks
            if local_risks is None:
                try:
                    local_risks = predict_all_risks(patient_data)
                except Exception as e:
                    st.error(f"No se pudo calcular el riesgo base para la simulación: {e}")
                    local_risks = None

            if local_risks is not None:
                aki = local_risks.get("aki_severe", {}).get("probability", 0)
                rrt = local_risks.get("rrt_needed", {}).get("probability", 0)
                mortality = local_risks.get("in_hospital_mortality", {}).get("probability", 0)

                real_states, base_matrix, matrix_df = build_transition_matrix_from_csv()

                # Asegurar consistencia global de estados
                if real_states != RENAL_STATES:
                    st.error("Los estados del CSV de Markov no coinciden con RENAL_STATES.")
                else:
                    initial_state_name = get_initial_markov_state_from_patient(patient_data, local_risks)
                    initial_state = RENAL_STATES.index(initial_state_name)

                    treatment_plan = {
                        "bp_control": bp_control,
                        "glucose_control": glucose_control,
                        "renal_protection": renal_protection,
                        "effect_strength": effect_strength
                    }

                    treated_matrix = apply_treatment_effects(base_matrix, patient_data, treatment_plan)

                    no_tx_path = simulate_markov_path(
                        initial_state_idx=initial_state,
                        transition_matrix=base_matrix,
                        steps=steps,
                        seed=int(seed_value)
                    )

                    no_tx_cohort = simulate_markov_cohort(
                        initial_state_idx=initial_state,
                        transition_matrix=base_matrix,
                        steps=steps,
                        n_simulations=int(n_simulations),
                        seed=int(seed_value)
                    )

                    tx_path = simulate_markov_path(
                        initial_state_idx=initial_state,
                        transition_matrix=treated_matrix,
                        steps=steps,
                        seed=int(seed_value) + 1
                    )

                    tx_cohort = simulate_markov_cohort(
                        initial_state_idx=initial_state,
                        transition_matrix=treated_matrix,
                        steps=steps,
                        n_simulations=int(n_simulations),
                        seed=int(seed_value) + 1
                    )

                    no_tx_prob_df = build_probability_evolution(no_tx_cohort)
                    tx_prob_df = build_probability_evolution(tx_cohort)
                    time_labels = get_time_labels(horizon_choice, steps)

                    st.session_state["dt_initial_state"] = initial_state
                    st.session_state["dt_initial_state_name"] = initial_state_name
                    st.session_state["dt_time_labels"] = time_labels
                    st.session_state["dt_no_tx_path"] = no_tx_path
                    st.session_state["dt_tx_path"] = tx_path
                    st.session_state["dt_no_tx_prob_df"] = no_tx_prob_df
                    st.session_state["dt_tx_prob_df"] = tx_prob_df
                    st.session_state["dt_base_matrix"] = base_matrix
                    st.session_state["dt_treated_matrix"] = treated_matrix

        if "dt_no_tx_prob_df" in st.session_state:
            initial_state = st.session_state["dt_initial_state"]
            initial_state_name = st.session_state["dt_initial_state_name"]
            time_labels = st.session_state["dt_time_labels"]

            no_tx_path = st.session_state["dt_no_tx_path"]
            tx_path = st.session_state["dt_tx_path"]

            no_tx_prob_df = st.session_state["dt_no_tx_prob_df"].copy()
            tx_prob_df = st.session_state["dt_tx_prob_df"].copy()

            base_matrix = st.session_state["dt_base_matrix"]
            treated_matrix = st.session_state["dt_treated_matrix"]

            no_tx_prob_df["Etiqueta tiempo"] = time_labels
            tx_prob_df["Etiqueta tiempo"] = time_labels

            st.markdown("## Estado inicial estimado")
            st.metric("Estado renal inicial", STATE_LABELS[initial_state_name])

            st.markdown("## Trayectoria simulada")
            traj_col1, traj_col2 = st.columns(2)

            with traj_col1:
                st.markdown("### Sin intervención")
                no_tx_path_df = pd.DataFrame({
                    "Tiempo": time_labels,
                    "Estado simulado": [STATE_LABELS[RENAL_STATES[s]] for s in no_tx_path],
                    "Código estado": no_tx_path
                })
                st.line_chart(no_tx_path_df.set_index("Tiempo")["Código estado"])

                st.markdown("#### Evolución anatómica estimada del riñón")
                cols = st.columns(min(5, len(no_tx_path)))
                step_indices = np.linspace(0, len(no_tx_path) - 1, num=len(cols), dtype=int)

                for i, idx in enumerate(step_indices):
                    state = RENAL_STATES[no_tx_path[idx]]
                    with cols[i]:
                        if state == "death":
                            st.warning("Estado terminal")
                        else:
                            try:
                                st.image(
                                    KIDNEY_IMAGES[state],
                                    caption=f"{time_labels[idx]}\n{STATE_LABELS[state]}",
                                    use_container_width=True
                                )
                            except Exception:
                                st.warning("Imagen no disponible")

            with traj_col2:
                st.markdown("### Con intervención")
                tx_path_df = pd.DataFrame({
                    "Tiempo": time_labels,
                    "Estado simulado": [STATE_LABELS[RENAL_STATES[s]] for s in tx_path],
                    "Código estado": tx_path
                })
                st.line_chart(tx_path_df.set_index("Tiempo")["Código estado"])

                st.markdown("#### Evolución anatómica estimada del riñón")
                cols = st.columns(min(5, len(tx_path)))
                step_indices = np.linspace(0, len(tx_path) - 1, num=len(cols), dtype=int)

                for i, idx in enumerate(step_indices):
                    state = RENAL_STATES[tx_path[idx]]
                    with cols[i]:
                        if state == "death":
                            st.warning("Estado terminal")
                        else:
                            try:
                                st.image(
                                    KIDNEY_IMAGES[state],
                                    caption=f"{time_labels[idx]}\n{STATE_LABELS[state]}",
                                    use_container_width=True
                                )
                            except Exception:
                                st.warning("Imagen no disponible")

            st.caption(
                "La representación visual muestra la progresión estimada del estado renal en el tiempo."
            )

            st.markdown("## Evolución probabilística por estado")
            prob_col1, prob_col2 = st.columns(2)

            with prob_col1:
                st.markdown("### Sin intervención")
                st.area_chart(no_tx_prob_df.set_index("Etiqueta tiempo")[RENAL_STATES])

            with prob_col2:
                st.markdown("### Con intervención")
                st.area_chart(tx_prob_df.set_index("Etiqueta tiempo")[RENAL_STATES])

            no_tx_final = no_tx_prob_df.iloc[-1]
            tx_final = tx_prob_df.iloc[-1]

            summary_compare = pd.DataFrame({
                "Estado": [STATE_LABELS[s] for s in RENAL_STATES],
                "Probabilidad final sin intervención": [no_tx_final[state] for state in RENAL_STATES],
                "Probabilidad final con intervención": [tx_final[state] for state in RENAL_STATES],
            })

            summary_compare["Cambio absoluto"] = (
                summary_compare["Probabilidad final con intervención"]
                - summary_compare["Probabilidad final sin intervención"]
            )

            st.markdown("## Comparación final del horizonte")
            st.dataframe(
                summary_compare.style.format({
                    "Probabilidad final sin intervención": "{:.2%}",
                    "Probabilidad final con intervención": "{:.2%}",
                    "Cambio absoluto": "{:+.2%}",
                }),
                use_container_width=True,
                height=260
            )

            no_tx_rrt = float(no_tx_final["rrt"])
            tx_rrt = float(tx_final["rrt"])
            no_tx_death = float(no_tx_final["death"])
            tx_death = float(tx_final["death"])

            st.markdown("## Interpretación comparativa")
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    "Terapia de reemplazo renal final",
                    f"{tx_rrt:.2%}",
                    delta=f"{(tx_rrt - no_tx_rrt):+.2%}"
                )

            with metric_col2:
                st.metric(
                    "Mortalidad final",
                    f"{tx_death:.2%}",
                    delta=f"{(tx_death - no_tx_death):+.2%}"
                )

            with metric_col3:
                favorable_states_no_tx = float(no_tx_final["stable"] + no_tx_final["ckd_no_aki"])
                favorable_states_tx = float(tx_final["stable"] + tx_final["ckd_no_aki"])
                st.metric(
                    "Estados favorables finales",
                    f"{favorable_states_tx:.2%}",
                    delta=f"{(favorable_states_tx - favorable_states_no_tx):+.2%}"
                )

            if tx_rrt < no_tx_rrt or tx_death < no_tx_death:
                st.success(
                    "La intervención simulada mejora el pronóstico frente al escenario sin tratamiento."
                )
            else:
                st.warning(
                    "La intervención simulada no muestra una mejoría clara con la configuración actual."
                )

            matrix_col1, matrix_col2 = st.columns(2)
            with matrix_col1:
                st.markdown("### Matriz sin intervención")
                st.dataframe(
                    pd.DataFrame(base_matrix, index=RENAL_STATES, columns=RENAL_STATES).rename(
                        index=STATE_LABELS, columns=STATE_LABELS
                    ).style.format("{:.2%}"),
                    use_container_width=True
                )

            with matrix_col2:
                st.markdown("### Matriz con intervención")
                st.dataframe(
                    pd.DataFrame(treated_matrix, index=RENAL_STATES, columns=RENAL_STATES).rename(
                        index=STATE_LABELS, columns=STATE_LABELS
                    ).style.format("{:.2%}"),
                    use_container_width=True
                )

    st.markdown("</div>", unsafe_allow_html=True)
