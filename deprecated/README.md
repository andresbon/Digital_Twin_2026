# Archivos Deprecados

Esta carpeta contiene archivos que fueron creados durante el desarrollo pero ya no se están utilizando en la versión actual del proyecto.

## Archivos Incluidos

### `digital_twin_bundle.py`
- **Propósito Original**: Definía la estructura del bundle entrenado
- **Razón de Deprecación**: Funcionalidad reemplazada por `bundle_schema.py` (versión mejorada con dataclass)
- **Estado**: Código cliente puede usar `bundle_schema.py` directamente

### `shap_engine.py`
- **Propósito Original**: Interpretabilidad de modelos usando SHAP (SHapley Additive exPlanations)
- **Razón de Deprecación**: Funcionalidad reemplazada por análisis con OpenAI API
- **Estado**: Considerado para futuras mejoras de interpretabilidad

### `treatment_simulator.py`
- **Propósito Original**: Simulador de tratamientos para pacientes
- **Razón de Deprecación**: Fuera del alcance actual (enfoque en predicción de riesgos)
- **Estado**: Posible para implementación futura

## Si Necesitas Recuperarlos

En caso de que necesites restaurar cualquiera de estos archivos:

```bash
# Desde la raíz del proyecto:
mv deprecated/nombre_archivo.py ./
```

## Para Limpiar Completamente

Si estás seguro de que no necesitas estos archivos:

```bash
rm -rf deprecated/
```

---

Actualizado: 8 de marzo de 2026
