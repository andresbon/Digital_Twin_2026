import pandas as pd
import joblib
import sys
import bundle_schema
from bundle_schema import DigitalTwinBundle
from clinical_features import ensure_all_features

# Registrar la clase en __main__ para que joblib pueda encontrarla
# (el archivo joblib fue guardado con la clase en __main__)
sys.modules['__main__'].DigitalTwinBundle = DigitalTwinBundle

bundle = joblib.load("digital_twin_bundle.joblib")

def predict_all_risks(patient_dict):
    df = pd.DataFrame([patient_dict])
    results = {}

    for target, model in bundle.models_by_target.items():
        features = bundle.features_by_target[target]
        X = ensure_all_features(df, features)

        print(f"\nTARGET: {target}")
        print("Features esperadas:", len(features))
        print("Features recibidas:", len(df.columns))

        missing = [f for f in features if f not in df.columns]
        print("Faltantes:", len(missing))
        print("Ejemplos faltantes:", missing[:15])

        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)
        pos_idx = classes.index(1)
        prob = float(proba[pos_idx])

        print("Probabilidad:", prob)

        results[target] = {
            "probability": prob
        }

    return results