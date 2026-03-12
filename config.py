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
