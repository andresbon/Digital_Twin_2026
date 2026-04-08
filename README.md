# 🧬 Digital Twin Dashboard — Renal Risk Monitor

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![License](https://img.shields.io/badge/License-Academic-lightgrey.svg)]()

Aplicación interactiva desarrollada en **Streamlit** para la evaluación, simulación y monitoreo del riesgo renal en pacientes con **hipertensión y/o diabetes**. La plataforma integra **Machine Learning**, **modelos de Markov** y una lógica de **Digital Twin** para representar la evolución clínica del paciente y comparar escenarios con y sin intervención terapéutica.

---

## 🚀 Descripción general

El sistema permite analizar el estado clínico de un paciente desde tres perspectivas complementarias:

- **Predicción individual de riesgo** mediante modelos de Machine Learning
- **Análisis comparativo** entre escenarios clínicos predefinidos
- **Evolución temporal** mediante simulación longitudinal basada en un modelo de Markov mensual

Además, la aplicación incluye una sección informativa de **Autores**, presentada en formato modal, con fotografía, rol profesional y perfil de cada integrante del proyecto.

---

## 🧭 Navegación principal de la aplicación

La interfaz principal organiza las acciones del usuario en el siguiente orden:

1. **Predecir condición del paciente**
2. **Instrucciones**
3. **Autores**

### Funcionalidad del botón "Autores"
El botón **Autores** abre un popup/modal informativo que muestra:

- Fotografía de cada autor
- Rol profesional
- Perfil académico y profesional

Esta sección fortalece la presentación institucional y académica del proyecto.

---

## ✨ Funcionalidades principales

### 🧑‍⚕️ Predicción individual
Permite ingresar datos clínicos del paciente de manera manual o mediante escenarios predefinidos para estimar tres desenlaces principales:

- **AKI severo**
- **Necesidad de terapia de reemplazo renal (RRT)**
- **Mortalidad intrahospitalaria**

Opcionalmente, el sistema puede complementar la salida con interpretación clínica asistida por IA si la configuración de OpenAI está habilitada.

### 📊 Análisis comparativo
Facilita la comparación entre distintos escenarios clínicos predefinidos para observar cómo cambian los riesgos estimados según las características del paciente.

Incluye:

- Visualización comparativa de riesgos
- Tabla de resultados
- Interpretación clínica comparada

### ⏳ Evolución temporal (Digital Twin)
Simula la trayectoria renal del paciente en el tiempo usando una **matriz de transición de Markov** construida a partir de datos longitudinales reales.

Estados clínicos utilizados:

- `stable`
- `ckd_no_aki`
- `aki_stage1`
- `aki_severe`
- `rrt`
- `death`

La simulación permite visualizar:

- Trayectoria temporal estimada
- Evolución probabilística mensual
- Estado más probable
- Comparación entre escenarios con y sin intervención
- Representación anatómica del riñón según el estado clínico

### 💊 Simulación de intervención
Permite modificar factores terapéuticos para comparar la evolución del paciente bajo diferentes intensidades de manejo clínico.

Parámetros ajustables:

- Control de presión arterial
- Control glucémico
- Protección renal
- Intensidad del tratamiento

### 🖼️ Visualización clínica
La aplicación incorpora imágenes médicas para reforzar la interpretación visual del estado renal del paciente a lo largo de la simulación.

---

## 📁 Estructura del proyecto

```text
digital_twin_dashboard/
├── 📄 app.py                      # Aplicación principal Streamlit
├── 🔧 config.py                   # Configuración general y autores
├── 🤖 ai_interpreter.py           # Interpretación clínica con OpenAI
├── 📊 risk_engine.py              # Motor de predicción ML
├── 📋 clinical_scenarios.py       # Escenarios clínicos predefinidos
├── 🏥 clinical_features.py        # Procesamiento y construcción de features
├── 📐 bundle_schema.py            # Estructura del bundle del modelo
├── 🔐 security_check.py           # Auditoría de seguridad
│
├── 🤖 digital_twin_bundle.joblib  # Modelo ML entrenado
├── requirements.txt
│
├── 📚 SETUP.md
├── README.md
│
├── 🔑 .env
├── 🔑 .env.example
├── .gitignore
│
├── 📂 data/                       # Datos para modelo de Markov
│   ├── markov_dataset_clean.csv
│   └── renal_markov_panel.csv
│
├── 📂 images/                     # Imágenes clínicas
│   ├── kidney_stable.png
│   ├── kidney_ckd_no_aki.png
│   ├── kidney_aki_stage1.png
│   ├── kidney_aki_severe.png
│   ├── kidney_rrt.png
│   ├── kidney_death.png
│   └── authors/
│       ├── autor1.jpg
│       ├── autor2.jpg
│       └── autor3.jpg
│
├── 📂 .streamlit/
│   └── config.toml               # Configuración visual de Streamlit
│
├── deprecated/
└── .venv/
```

---

## ⚡ Quick Start

### 0. Descargar el Modelo Entrenado

El archivo `digital_twin_bundle.joblib` no está incluido en el repositorio por su tamaño.

**Debes colocarlo manualmente en la raíz del proyecto:**


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

## 🧠 Arquitectura del sistema

Input del paciente
   ↓
Procesamiento de variables clínicas
   ↓
Modelo ML entrenado (joblib)
   ↓
Predicción de riesgos
   ↓
Asignación del estado renal inicial
   ↓
Modelo de Markov basado en datos longitudinales
   ↓
Simulación temporal del paciente
   ↓
Visualización clínica + comparación de intervención

## 📊 Datos utilizados
**MIMIC-IV**

La aplicación se apoya en datos clínicos reales derivados de MIMIC-IV, utilizados para construir el componente longitudinal del modelo.

Incluye:

- Cohorte hospitalaria real
- Variables clínicas y laboratoriales
- Estados renales observados en el tiempo

**Panel longitudinal renal**
Se utiliza un panel mensual por paciente para estimar transiciones entre estados renales y construir la simulación tipo Digital Twin.

## 🔄 Matriz de transición de Markov

La matriz de transición se construye a partir de observaciones consecutivas por paciente usando una estructura longitudinal mensual.

Ejemplo de lógica empleada:
```bash
LEAD(markov_state) OVER (PARTITION BY subject_id ORDER BY calendar_month)
```
Filtrando transiciones consecutivas con:
```bash
gap_months = 1
```

## ⚙️ Configuración visual

Archivo de configuración:

```bash
.streamlit/config.toml

[theme]
base="light"
```
Esta configuración permite:

- Forzar modo claro
- Mejorar legibilidad clínica
- Mantener consistencia visual de la interfaz

## 🤖 Modelos utilizados

El bundle principal contiene tres modelos entrenados:

- aki_severe
- rrt_needed
- in_hospital_mortality

Cada modelo puede incluir componentes como:

- Preprocesamiento de variables
- Escalado
- Balanceamiento de clases
- Clasificador final

## 📂 Carpeta data/

Contiene:

- markov_dataset_clean.csv → matriz de transición
- renal_markov_panel.csv → panel longitudinal

## 📂 Carpeta images/

Contiene imágenes médicas para representar:

- Estados renales
- Evolución anatómica
- Interpretación visual del modelo

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

## ⚠️ Disclaimer
- Herramienta desarrollada con fines de investigación académica
- No sustituye la valoración médica profesional
- La simulación de intervención no representa causalidad clínica real
- Los resultados deben interpretarse como apoyo analítico y no como decisión clínica final

## 📝 Cambios Recientes

- ✅ Integración modelo Markov real (MIMIC-IV)
- ✅ Pestaña de evolución temporal (Digital Twin)
- ✅ Simulación tratamiento vs no tratamiento
- ✅ Visualización anatómica del riñón
- ✅ Carpeta data/
- ✅ Carpeta images/
- ✅ Configuración .streamlit (modo claro)
- ✅ Mejora UX/UI clínica
- ✅ Nueva carpeta images/authors/
- ✅ Nuevo botón Autores
- ✅ Popup/modal de autores con foto, rol y perfil profesional
- ✅ Reorganización de acciones principales en la interfaz
- ✅ Mejora de experiencia visual y presentación institucional

## 📖 Licencia

Este proyecto es parte de la investigación en Digital Twin para predicción de riesgos renales.

## 👥 Autores del proyecto
**Santiago González Cruz**

**Matemático | Ciencia de Datos e Inteligencia Artificial**
Especialista en ciencia de datos, inteligencia artificial, automatización y modelado matemático aplicado a problemas complejos en salud y analítica predictiva.

**Angel Andrés Bonilla Bonilla**

**Ingeniero de Sistemas | Calidad de Software y DevSecOps**
Profesional con amplia experiencia en calidad de software, automatización, gobierno de calidad y fortalecimiento de la resiliencia tecnológica en entornos corporativos.

**Diana Natalia Cerinza Suescun**

Médica | Epidemiología y Administración en Salud
Profesional con experiencia en investigación, gestión del riesgo en salud, epidemiología y administración de servicios de salud, con enfoque en sostenibilidad y optimización de recursos.

---

**Aplicación creada**: 8 de marzo de 2026  
**Última actualización**: 28 de marzo de 2026
