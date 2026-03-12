# Escenarios clínicos para análisis comparativo

CLINICAL_SCENARIOS = {
    "1. Paciente Sano": {
        "description": "Adulto sin comorbilidades",
        "gender": 1,  # Masculino
        "age": 45,
        "anchor_year_group": 1,  # 2013-2017
        "hypertension_flag": 0,
        "diabetes_flag": 0,
        "ckd_flag": 0,
        "creatinine": 0.9,
        "bun": 15,
        "sodium": 138,
        "potassium": 4.0,
        "hemoglobin": 14.5,
        "sbp_mean": 120,
        "dbp_mean": 75,
        "heart_rate_mean": 70,
    },
    
    "2. Hipertensión Controlada": {
        "description": "Paciente con hipertensión bien controlada",
        "gender": 1,  # Masculino
        "age": 58,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 1,
        "diabetes_flag": 0,
        "ckd_flag": 0,
        "creatinine": 1.0,
        "bun": 18,
        "sodium": 137,
        "potassium": 4.1,
        "hemoglobin": 14.0,
        "sbp_mean": 135,
        "dbp_mean": 82,
        "heart_rate_mean": 75,
    },
    
    "3. Diabetes Tipo 2": {
        "description": "Paciente diabético sin otras comorbilidades",
        "gender": 0,  # Femenino
        "age": 62,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 0,
        "diabetes_flag": 1,
        "ckd_flag": 0,
        "creatinine": 1.1,
        "bun": 20,
        "sodium": 136,
        "potassium": 4.2,
        "hemoglobin": 13.8,
        "sbp_mean": 128,
        "dbp_mean": 78,
        "heart_rate_mean": 78,
    },
    
    "4. Diabetes e Hipertensión": {
        "description": "Paciente con diabetes e hipertensión",
        "gender": 1,  # Masculino
        "age": 70,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 0,
        "creatinine": 1.3,
        "bun": 22,
        "sodium": 135,
        "potassium": 4.4,
        "hemoglobin": 13.2,
        "sbp_mean": 145,
        "dbp_mean": 85,
        "heart_rate_mean": 82,
    },
    
    "5. Enfermedad Renal Crónica Estadio 3": {
        "description": "Paciente con ERC estadio 3 (moderada)",
        "gender": 0,  # Femenino
        "age": 72,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 1,
        "creatinine": 1.8,
        "bun": 28,
        "sodium": 134,
        "potassium": 4.6,
        "hemoglobin": 11.5,
        "sbp_mean": 152,
        "dbp_mean": 88,
        "heart_rate_mean": 85,
    },
    
    "6. Enfermedad Renal Crónica Avanzada": {
        "description": "Paciente con ERC estadio 4 (severa)",
        "gender": 1,  # Masculino
        "age": 68,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 1,
        "creatinine": 3.2,
        "bun": 45,
        "sodium": 132,
        "potassium": 5.2,
        "hemoglobin": 9.5,
        "sbp_mean": 160,
        "dbp_mean": 92,
        "heart_rate_mean": 88,
    },
    
    "7. Paciente Crítico": {
        "description": "Paciente de alto riesgo con múltiples comorbilidades",
        "gender": 0,  # Femenino
        "age": 78,
        "anchor_year_group": 2,  # 2018-2022
        "hypertension_flag": 1,
        "diabetes_flag": 1,
        "ckd_flag": 1,
        "creatinine": 2.9,
        "bun": 52,
        "sodium": 130,
        "potassium": 5.5,
        "hemoglobin": 8.8,
        "sbp_mean": 170,
        "dbp_mean": 95,
        "heart_rate_mean": 95,
    },
}


def get_scenario_details(scenario_name):
    """Obtiene los detalles de un escenario clínico"""
    return CLINICAL_SCENARIOS.get(scenario_name)


def get_all_scenarios():
    """Retorna todos los escenarios disponibles"""
    return CLINICAL_SCENARIOS
