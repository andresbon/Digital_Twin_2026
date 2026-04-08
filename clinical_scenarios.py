CLINICAL_SCENARIOS = {
    "1. HTA Estable": {
        "description": "Paciente con hipertensión arterial sin diabetes, con función renal conservada y estabilidad clínica general.",
        "gender": 1,  # Masculino
        "age": 56,
        "hypertension_flag": 1,
        "diabetes_flag": 0,
        "ckd_flag": 0,
        "creatinine": 1.0,
        "bun": 18,
        "sodium": 138,
        "potassium": 4.2,
        "hemoglobin": 14.0,
        "sbp_mean": 132,
        "dbp_mean": 82,
        "heart_rate_mean": 74,
        "chloride": 102,
        "bicarbonate": 24,
        "glucose_lab": 98,
        "calcium": 9.1,
        "hematocrit": 42.0,
        "wbc": 7.2,
        "platelet": 245,
        "mbp_mean": 99,
        "resp_rate_mean": 16,
        "temperature_mean": 36.7,
        "spo2_mean": 97
    },

    "2. Diabetes Controlada": {
        "description": "Paciente con diabetes mellitus tipo 2, sin compromiso hemodinámico importante y con función renal aún conservada.",
        "gender": 1,  # Masculino
        "age": 59,
        "hypertension_flag": 0,
        "diabetes_flag": 1,
        "ckd_flag": 0,
        "creatinine": 1.1,
        "bun": 20,
        "sodium": 137,
        "potassium": 4.3,
        "hemoglobin": 13.5,
        "sbp_mean": 124,
        "dbp_mean": 78,
        "heart_rate_mean": 78,
        "chloride": 101,
        "bicarbonate": 23,
        "glucose_lab": 145,
        "calcium": 9.0,
        "hematocrit": 40.5,
        "wbc": 7.8,
        "platelet": 240,
        "mbp_mean": 93,
        "resp_rate_mean": 16,
        "temperature_mean": 36.8,
        "spo2_mean": 97
    },

    "3. Diabetes + HTA Moderada": {
        "description": "Paciente con diabetes e hipertensión, con alteraciones metabólicas y renales moderadas, compatible con un riesgo intermedio de eventos renales.",
        "gender": 1,  # Masculino
        "age": 64,
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 0,
        "creatinine": 1.5,
        "bun": 26,
        "sodium": 136,
        "potassium": 4.7,
        "hemoglobin": 12.8,
        "sbp_mean": 144,
        "dbp_mean": 86,
        "heart_rate_mean": 82,
        "chloride": 100,
        "bicarbonate": 21,
        "glucose_lab": 210,
        "calcium": 8.9,
        "hematocrit": 38.0,
        "wbc": 8.9,
        "platelet": 228,
        "mbp_mean": 105,
        "resp_rate_mean": 18,
        "temperature_mean": 36.9,
        "spo2_mean": 96
    },

    "4. Diabetes + HTA con Riesgo Renal Aumentado": {
        "description": "Paciente con diabetes e hipertensión, con cambios clínicos y de laboratorio que sugieren mayor vulnerabilidad renal y mayor probabilidad de eventos adversos intrahospitalarios.",
        "gender": 1,  # Masculino
        "age": 68,
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 1,
        "creatinine": 2.2,
        "bun": 40,
        "sodium": 134,
        "potassium": 5.1,
        "hemoglobin": 11.3,
        "sbp_mean": 118,
        "dbp_mean": 72,
        "heart_rate_mean": 96,
        "chloride": 98,
        "bicarbonate": 18,
        "glucose_lab": 235,
        "calcium": 8.6,
        "hematocrit": 34.0,
        "wbc": 11.5,
        "platelet": 210,
        "mbp_mean": 87,
        "resp_rate_mean": 22,
        "temperature_mean": 37.5,
        "spo2_mean": 93
    },

    "5. Diabetes + HTA con Alto Riesgo de Eventos Renales": {
        "description": "Paciente con diabetes e hipertensión de larga evolución, antecedente de enfermedad renal crónica y perfil clínico compatible con alto riesgo de lesión renal aguda, necesidad de terapia de reemplazo renal y desenlaces hospitalarios adversos.",
        "gender": 1,  # Masculino
        "age": 74,
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 1,
        "creatinine": 4.2,
        "bun": 82,
        "sodium": 130,
        "potassium": 6.0,
        "hemoglobin": 9.2,
        "sbp_mean": 92,
        "dbp_mean": 58,
        "heart_rate_mean": 114,
        "chloride": 95,
        "bicarbonate": 12,
        "glucose_lab": 260,
        "calcium": 8.0,
        "hematocrit": 29.0,
        "wbc": 15.5,
        "platelet": 185,
        "mbp_mean": 69,
        "resp_rate_mean": 28,
        "temperature_mean": 38.1,
        "spo2_mean": 89
    },
}


def get_scenario_details(scenario_name):
    """Obtiene los detalles de un escenario clínico"""
    return CLINICAL_SCENARIOS.get(scenario_name)


def get_all_scenarios():
    """Retorna todos los escenarios disponibles"""
    return CLINICAL_SCENARIOS