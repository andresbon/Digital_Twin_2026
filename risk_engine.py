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

        prob = model.predict_proba(X)[0][1]

        results[target] = {
            "probability": float(prob)
        }

    return results