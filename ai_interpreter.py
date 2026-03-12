from openai import OpenAI
from config import OPENAI_API_KEY, is_openai_configured


def generate_clinical_interpretation(patient_data, risks):
    """
    Genera una interpretación clínica mejorada usando OpenAI API
    
    Args:
        patient_data: Dict con los datos del paciente
        risks: Dict con los riesgos predichos
    
    Returns:
        str: Interpretación clínica en español
    """
    
    if not is_openai_configured():
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Preparar prompt con información del paciente
        prompt = f"""
        Analiza el siguiente caso clínico y proporciona una interpretación detallada en español.
        
        **DATOS DEL PACIENTE:**
        - Edad: {patient_data.get('age', 'N/A')} años
        - Género: {'Masculino' if patient_data.get('gender') == 1 else 'Femenino'}
        - Hipertensión: {'Sí' if patient_data.get('hypertension_flag') == 1 else 'No'}
        - Diabetes: {'Sí' if patient_data.get('diabetes_flag') == 1 else 'No'}
        - Enfermedad Renal Crónica: {'Sí' if patient_data.get('ckd_flag') == 1 else 'No'}
        - Creatinina: {patient_data.get('creatinine', 'N/A')} mg/dL
        - BUN: {patient_data.get('bun', 'N/A')} mg/dL
        - Hemoglobina: {patient_data.get('hemoglobin', 'N/A')} g/dL
        - Presión Arterial Sistólica: {patient_data.get('sbp_mean', 'N/A')} mmHg
        - Frecuencia Cardíaca: {patient_data.get('heart_rate_mean', 'N/A')} bpm
        
        **PREDICCIONES DEL MODELO:**
        - Riesgo de Lesión Renal Aguda Severa: {risks.get('aki_severe', {}).get('probability', 0):.2%}
        - Riesgo de Terapia de Reemplazo Renal: {risks.get('rrt_needed', {}).get('probability', 0):.2%}
        - Riesgo de Mortalidad Intrahospitalaria: {risks.get('in_hospital_mortality', {}).get('probability', 0):.2%}
        
        Por favor proporciona:
        1. Un resumen clínico de la condición general del paciente
        2. Factores de riesgo principales identificados
        3. Recomendaciones de seguimiento y manejo
        4. Consideraciones especiales para este caso
        
        Mantén la respuesta concisa, profesional y orientada al clínico.
        """
        
        message = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto médico especializado en nefrología e interpretación de datos clínicos. Proporcionas análisis médicos profesionales y detallados."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        
        return message.choices[0].message.content
    
    except Exception as e:
        return f"Error al generar interpretación con IA: {str(e)}"


def generate_scenario_comparison(scenarios_data, results_data):
    """
    Genera un análisis comparativo de escenarios usando OpenAI
    
    Args:
        scenarios_data: List de dict con datos de escenarios
        results_data: Dict con resultados de predicciones
    
    Returns:
        str: Análisis comparativo en español
    """
    
    if not is_openai_configured():
        return None
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Preparar información de escenarios
        scenarios_text = ""
        for i, scenario in enumerate(results_data.get('Escenario', [])):
            aki = results_data.get('AKI', [])[i] if i < len(results_data.get('AKI', [])) else 0
            rrt = results_data.get('RRT', [])[i] if i < len(results_data.get('RRT', [])) else 0
            mort = results_data.get('Mortalidad', [])[i] if i < len(results_data.get('Mortalidad', [])) else 0
            scenarios_text += f"\n{i+1}. {scenario}: AKI={aki:.2%}, RRT={rrt:.2%}, Mortalidad={mort:.2%}"
        
        prompt = f"""
        Analiza la siguiente comparación de escenarios clínicos y proporciona recomendaciones basadas en los perfiles de riesgo.
        
        **ESCENARIOS COMPARADOS:**{scenarios_text}
        
        Por favor proporciona:
        1. Comparación de riesgos entre escenarios
        2. Patrones clínicos principales
        3. Implicaciones para la gestión clínica
        4. Recomendaciones de priorización de pacientes
        5. Factores modificables en cada grupo
        
        Mantén el análisis conciso, profesional y orientado a la práctica clínica.
        """
        
        message = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de datos clínicos y medicina basada en evidencia. Proporciona insights clínicos valiosos y accionables."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        return message.choices[0].message.content
    
    except Exception as e:
        return f"Error al generar análisis con IA: {str(e)}"
