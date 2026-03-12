import pandas as pd


def build_patient_dataframe(patient_dict):

    df = pd.DataFrame([patient_dict])

    return df


def ensure_all_features(df, features):

    return df.reindex(columns=features, fill_value=0)