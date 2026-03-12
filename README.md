# 🧬 Digital Twin Dashboard — Monitor de Riesgo Renal

Una aplicación interactiva basada en Streamlit para predicción de riesgos clínicos en pacientes renales usando modelos de machine learning y análisis mejorados con IA.

## 📋 Estructura del Proyecto

```
digital_twin_dashboard/
├── 📄 app.py                      # Aplicación principal Streamlit
├── 🔧 config.py                   # Configuración de variables de entorno
├── 🤖 ai_interpreter.py           # Análisis mejorado con OpenAI API
├── 📊 risk_engine.py              # Motor de predicción de riesgos
├── 📋 clinical_scenarios.py       # Escenarios clínicos predefinidos
├── 🏥 clinical_features.py        # Procesamiento de características clínicas
├── 📐 bundle_schema.py            # Definición de estructura de data
├── 🔐 security_check.py           # Script de auditoría de seguridad
│
├── 🤖 digital_twin_bundle.joblib  # Modelo entrenado (datos, 2.5MB)
├── requirements.txt               # Dependencias Python
│
├── 📚 SETUP.md                    # Guía de configuración de OpenAI
├── README.md                      # Este archivo
│
├── 🔑 .env                        # Variables de entorno (LOCAL, no compartir)
├── 🔑 .env.example                # Template de .env (para compartir)
├── .gitignore                     # Archivos a ignorar en Git
│
├── deprecated/                    # Archivos no utilizados
│   ├── digital_twin_bundle.py
│   ├── shap_engine.py
│   ├── treatment_simulator.py
│   └── README.md
│
└── .venv/                         # Entorno virtual Python
```

## ⚡ Quick Start

### 0. Descargar el Modelo Entrenado

El archivo `digital_twin_bundle.joblib` (509 MB) no está incluido en el repositorio por su tamaño. 

**Necesitas descargarlo manualmente:**

1. Descarga el archivo desde tu almacenamiento local o nube
2. Colócalo en la raíz del proyecto: `/digital_twin_dashboard/digital_twin_bundle.joblib`

> **Alternativa:** Si no tienes el archivo, puedes entrenar tu propio modelo editando `deprecated/digital_twin_bundle.py`

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI (Opcional)
```bash
# Copiar template
cp .env.example .env

# Editar .env y agregar tu API key
# OPENAI_API_KEY=sk-proj-xxxxx
```

### 3. Ejecutar la Aplicación
```bash
streamlit run app.py
```

Abre tu navegador en: `http://localhost:8501`

## 🚀 Características Principales

### 📊 Predicción Individual
- Entrada manual de parámetros clínicos
- Escenarios predefinidos
- Predicción de 3 tipos de riesgo:
  - 🔴 Lesión Renal Aguda Severa (AKI)
  - 💧 Necesidad de Terapia de Reemplazo Renal (RRT)
  - ⚠️ Mortalidad Intrahospitalaria
- Análisis clínico mejorado con IA (si OpenAI está configurado)

### 📈 Análisis Comparativo
- Comparación entre 7 escenarios clínicos
- Gráficos interactivos
- Tabla de resultados
- Análisis comparativo con IA

### 🔐 Seguridad
- API key protegida en `.env`
- Script de auditoría de seguridad
- Validación de configuración

## 📊 Escenarios Clínicos Predefinidos

1. **Paciente Sano** - Sin comorbilidades
2. **Hipertensión Controlada** - Presión elevada
3. **Diabetes Tipo 2** - Glucemia alterada
4. **Diabetes e Hipertensión** - Múltiples factores
5. **ERC Estadio 3** - Enfermedad renal crónica moderada
6. **ERC Avanzada** - Enfermedad renal crónica severa
7. **Paciente Crítico** - Alto riesgo multifactorial

## 🔧 Arquitectura Técnica

### Pipeline de Predicción
```
patient_data (dict)
    ↓
ensure_all_features() [clinical_features.py]
    ↓
DigitalTwinBundle models [digital_twin_bundle.joblib]
    ↓
predict_all_risks() [risk_engine.py]
    ↓
risks (dict con probabilidades)
    ↓
generate_clinical_interpretation() [ai_interpreter.py + OpenAI]
    ↓
Análisis clínico detallado
```

### Dependencias Principales
- **streamlit** - Framework web interactivo
- **pandas, numpy** - Procesamiento de datos
- **scikit-learn, imblearn** - ML pipelines
- **joblib** - Serialización de modelos
- **plotly** - Gráficos interactivos
- **openai** - API de análisis con IA
- **python-dotenv** - Manejo de variables de entorno

## 🔐 Configuración de Seguridad

### Protección de API Keys
```bash
# ✅ Correcto: Variables de entorno
OPENAI_API_KEY=sk-proj-xxxxx  # En archivo .env

# ❌ Incorrecto: Hardcoded
OPENAI_API_KEY = "sk-proj-xxxxx"  # En el código fuente
```

### Verificar Seguridad
```bash
python security_check.py
```

## 📚 Documentación Adicional

- **SETUP.md** - Guía completa de configuración de OpenAI
- **deprecated/README.md** - Información sobre archivos anteriores
- Cada archivo Python contiene docstrings detallados

## 🔄 Modelos Utilizados

El bundle contiene 3 modelos entrenados:
- **aki_severe**: Predice lesión renal aguda severa
- **rrt_needed**: Predice necesidad de terapia de reemplazo renal
- **in_hospital_mortality**: Predice mortalidad intrahospitalaria

Cada modelo usa un pipeline sklearn/imblearn que incluye:
- Preprocesamiento de features
- Escalado
- Balanceamiento de clases
- Algoritmo de clasificación

## 🤝 Contribuciones

Para mejorar el proyecto:

1. Verifica seguridad: `python security_check.py`
2. Instala dependencias: `pip install -r requirements.txt`
3. Realiza cambios en tu rama
4. Prueba localmente: `streamlit run app.py`

## 📝 Cambios Recientes

- ✅ Integración con OpenAI API para análisis mejorado
- ✅ 7 escenarios clínicos predefinidos
- ✅ Análisis comparativo interactivo
- ✅ Limpieza de código (archivos deprecados movidos)
- ✅ Guía de seguridad completa

## 📖 Licencia

Este proyecto es parte de la investigación en Digital Twin para predicción de riesgos renales.

---

**Aplicación creada**: 8 de marzo de 2026  
**Última actualización**: 8 de marzo de 2026
