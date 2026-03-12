import shap
import pandas as pd
from clinical_features import ensure_all_features


def explain_prediction(bundle, patient_dict, target):

    model = bundle.models_by_target[target]

    features = bundle.features_by_target[target]

    df = pd.DataFrame([patient_dict])

    X = ensure_all_features(df, features)

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(X)

    return shap_values, X