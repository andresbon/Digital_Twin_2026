import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
APP_NAME = os.getenv("APP_NAME", "Digital Twin Dashboard")


def is_openai_configured():
    """Verifica si OpenAI está configurado"""
    return bool(OPENAI_API_KEY and OPENAI_API_KEY != "tu_clave_api_aqui")


# Umbrales mínimos de coherencia para simulación
HTN_MIN_SBP = 130   # Presión sistólica mínima si marca hipertensión
HTN_MIN_DBP = 80    # Presión diastólica mínima si marca hipertensión
HTN_MIN_MBP = 90    # Presión arterial media mínima si marca hipertensión

DM_MIN_GLUCOSE = 126.0  # Glucosa mínima si marca diabetes


# Rangos globales realistas
DEFAULT_RANGES = {
    # Parámetros laborales
    "creatinine": {
        "min": 0.3,
        "max": 15.0,
        "value": 1.2,
        "step": 0.1
    },
    "bun": {
        "min": 5.0,
        "max": 100.0,
        "value": 20.0,
        "step": 1.0
    },
    "sodium": {
        "min": 120.0,
        "max": 160.0,
        "value": 138.0,
        "step": 1.0
    },
    "potassium": {
        "min": 2.5,
        "max": 7.0,
        "value": 4.0,
        "step": 0.1
    },
    "hemoglobin": {
        "min": 5.0,
        "max": 18.0,
        "value": 11.0,
        "step": 0.1
    },

    # Signos vitales principales
    "sbp_mean": {
        "min": 80,
        "max": 250,
        "value": 120,
        "step": 1
    },
    "dbp_mean": {
        "min": 40,
        "max": 150,
        "value": 80,
        "step": 1
    },
    "mbp_mean": {
        "min": 55,
        "max": 180,
        "value": 93,
        "step": 1
    },
    "heart_rate_mean": {
        "min": 30,
        "max": 180,
        "value": 80,
        "step": 1
    },

    # Laboratorios adicionales
    "chloride": {
        "min": 80.0,
        "max": 130.0,
        "value": 102.0,
        "step": 1.0
    },
    "bicarbonate": {
        "min": 5.0,
        "max": 40.0,
        "value": 24.0,
        "step": 1.0
    },
    "glucose_lab": {
        "min": 70.0,
        "max": 500.0,
        "value": 110.0,
        "step": 1.0
    },
    "calcium": {
        "min": 5.0,
        "max": 13.0,
        "value": 9.0,
        "step": 0.1
    },
    "hematocrit": {
        "min": 15.0,
        "max": 60.0,
        "value": 36.0,
        "step": 0.1
    },
    "wbc": {
        "min": 0.5,
        "max": 50.0,
        "value": 8.0,
        "step": 0.1
    },
    "platelet": {
        "min": 10.0,
        "max": 1000.0,
        "value": 250.0,
        "step": 1.0
    },

    # Signos vitales adicionales
    "resp_rate_mean": {
        "min": 8,
        "max": 40,
        "value": 18,
        "step": 1
    },
    "temperature_mean": {
        "min": 34.0,
        "max": 41.0,
        "value": 36.8,
        "step": 0.1
    },
    "spo2_mean": {
        "min": 70,
        "max": 100,
        "value": 98,
        "step": 1
    }
}

AUTHORS = [
    {
        "name": "Santiago González Cruz",
        "role": "Matemático | Ciencia de Datos e Inteligencia Artificial",
        "photo": "images/authors/autor1.jpg",
        "profile": (
            "Matemático con más de tres años de experiencia en ciencia de datos, "
            "inteligencia artificial y analítica avanzada. Especializado en diseño "
            "y optimización de bases de datos, procesos ETL, automatización, "
            "modelado matemático y desarrollo de algoritmos predictivos orientados "
            "a la toma de decisiones."
        ),
    },
    {
        "name": "Angel Andrés Bonilla Bonilla",
        "role": "Ingeniero de Sistemas | Calidad de Software y DevSecOps",
        "photo": "images/authors/autor2.jpg",
        "profile": (
            "Director de Calidad de Software con más de 12 años de experiencia en "
            "los sectores financiero y fintech. Especializado en gobierno de calidad, "
            "automatización inteligente, DevSecOps y análisis preventivo de código "
            "para fortalecer la estabilidad operativa, reducir riesgos tecnológicos "
            "y optimizar la entrega de soluciones."
        ),
    },
    {
        "name": "Diana Natalia Cerinza Suescun",
        "role": "Médica | Epidemiología y Administración en Salud",
        "photo": "images/authors/autor3.jpg",
        "profile": (
            "Médica de la Universidad Pedagógica y Tecnológica de Colombia, "
            "especialista en Epidemiología de la Universidad El Bosque y magíster "
            "en Administración en Salud de la Universidad del Rosario. Cuenta con "
            "15 años de experiencia en los ámbitos asistencial y administrativo, "
            "liderando procesos de coordinación, investigación, monitorización "
            "estratégica e implementación de modelos de prestación de servicios en salud."
        ),
    },
]