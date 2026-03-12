# 🚀 Guía de Configuración - Digital Twin Dashboard

## Configuración de OpenAI API (Opcional pero Recomendado)

Para habilitar los análisis clínicos mejorados con IA, necesitas configurar tu API key de OpenAI.

### Paso 1: Obtener tu API Key de OpenAI

1. **Crea una cuenta en OpenAI** (si no tienes una):
   - Ve a https://platform.openai.com
   - Haz clic en "Sign Up" y crea una cuenta

2. **Obtén tu API Key**:
   - Una vez logueado, ve a https://platform.openai.com/account/api-keys
   - Haz clic en "Create new secret key"
   - Copia la clave generada (asegúrate de guardarla en un lugar seguro)

### Paso 2: Configurar la API Key en el Proyecto

Hay **dos formas** de configurar tu API key:

#### Opción A: Archivo `.env` (Recomendado para desarrollo local)

1. **Crea un archivo `.env`** en la raíz del proyecto:
   ```bash
   cd /Users/bon9418/Documents/digital_twin_dashboard
   cp .env.example .env
   ```

2. **Edita el archivo `.env`** con tu editor de texto preferido:
   ```env
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   APP_NAME=Digital Twin Dashboard
   ```

   **Reemplaza `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` con tu API key real.**

3. **Guarda el archivo** (Ctrl+S o Cmd+S)

4. **Importante**: El archivo `.env` está incluido en `.gitignore` para proteger tu API key. Nunca lo compartas públicamente.

#### Opción B: Variables de Entorno del Sistema

Si prefieres no usar un archivo `.env`, puedes configurar variables de entorno directamente:

**En macOS/Linux (Terminal):**
```bash
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**En Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Luego, reinicia la aplicación Streamlit.

### Paso 3: Verificar la Configuración

1. **Reinicia la aplicación**:
   ```bash
   # Presiona Ctrl+C en la terminal donde corre Streamlit
   # Luego ejecuta nuevamente:
   streamlit run app.py
   ```

2. **Verifica que funciona**:
   - En la pestaña **"Predicción Individual"**, después de hacer una predicción, deberías ver la sección **"🤖 Análisis Clínico con IA"**
   - En la pestaña **"Análisis Comparativo"**, después de ejecutar el análisis, verás **"🤖 Análisis Comparativo con IA"**

3. **Si ves un mensaje de error**:
   - Verifica que tu API key sea correcta
   - Comprueba que tengas créditos disponibles en tu cuenta de OpenAI
   - Asegúrate de que el archivo `.env` esté en la raíz del proyecto

### Paso 4: Entender los Costos

- OpenAI ofrece un **crédito inicial gratuito** ($5-$18) para nuevas cuentas durante 3 meses
- Después, se cobra por uso: 
  - **GPT-3.5-turbo**: ~$0.0015 por 1K tokens de entrada, ~$0.002 por 1K tokens de salida
  - El costo por predicción es típicamente muy bajo (~$0.01-$0.05)

### Paso 5: Seguridad

⚠️ **IMPORTANTE**: 
- Nunca compartas tu API key públicamente
- No la incluyas en comandos git
- Si accidentalmente expusiste tu clave, regenérala inmediatamente en https://platform.openai.com/account/api-keys

## Estructura de Archivos de Configuración

```
digital_twin_dashboard/
├── .env                    # ← Tu API key va aquí (NO compartir)
├── .env.example            # ← Plantilla (puede compartirse)
├── config.py               # ← Carga las variables de .env
├── ai_interpreter.py       # ← Funciones que usan OpenAI
├── app.py                  # ← Aplicación principal
├── requirements.txt        # ← Dependencias (incluye openai, python-dotenv)
└── ...
```

## Solución de Problemas

### "No se pudo generar el análisis con IA"

**Solución 1**: Verifica que tu API key sea correcta
```python
# En la terminal, ejecuta:
python -c "from config import OPENAI_API_KEY; print('API Key configurada:', bool(OPENAI_API_KEY))"
```

**Solución 2**: Verifica la conexión a internet
```bash
ping platform.openai.com
```

**Solución 3**: Reinicia Streamlit
```bash
# Presiona Ctrl+C en la terminal
streamlit run app.py
```

### "ImportError: No module named 'openai'"

Instala las dependencias nuevamente:
```bash
pip install -r requirements.txt
```

## Contacto y Soporte

Para reportar problemas con OpenAI API:
- Visita: https://status.openai.com
- Lee la documentación: https://platform.openai.com/docs/api-reference

---

**¡Listo!** Ahora tu aplicación debería tener análisis clínicos mejorados con IA. 🎉
