import numpy as np
import pandas as pd
from risk_engine import predict_all_risks


def simulate_treatment(bundle, patient_data, steps=12):

    timeline = []

    current = patient_data.copy()

    for t in range(steps):

        # simulación tratamiento
        current["glucosa"] *= np.random.uniform(0.97, 0.99)
        current["presion"] *= np.random.uniform(0.98, 0.995)

        pred = predict_all_risks(bundle, current)

        timeline.append({
            k: v["probability"] for k, v in pred.items()
        })

    return pd.DataFrame(timeline)