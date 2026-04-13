from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestModel:
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)

    def fit(self, x):
        self.model.fit(x)

    def predict_score(self, x):
        decision = self.model.decision_function(x)
        # Convert to probability-like anomaly score in [0,1].
        return 1.0 / (1.0 + np.exp(5.0 * decision))

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @staticmethod
    def load(path: Path):
        model = IsolationForestModel()
        model.model = joblib.load(path)
        return model
