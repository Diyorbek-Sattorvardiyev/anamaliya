from pathlib import Path

import joblib
import numpy as np
from sklearn.neural_network import MLPRegressor


class AutoencoderModel:
    def __init__(self, input_dim: int):
        self.model = MLPRegressor(
            hidden_layer_sizes=(16, 8, 4, 8, 16),
            activation="relu",
            solver="adam",
            learning_rate_init=1e-3,
            max_iter=1,
            warm_start=True,
            random_state=42,
        )
        self.input_dim = input_dim
        self.threshold = 0.0

    def fit(self, x: np.ndarray, epochs: int = 20, batch_size: int = 128, lr: float = 1e-3):
        self.model.learning_rate_init = lr
        for _ in range(epochs):
            self.model.fit(x, x)

        errors = self.reconstruction_error(x)
        self.threshold = float(np.percentile(errors, 95))

    def reconstruction_error(self, x: np.ndarray) -> np.ndarray:
        recon = self.model.predict(x)
        return np.mean((recon - x) ** 2, axis=1)

    def predict_score(self, x: np.ndarray) -> np.ndarray:
        errors = self.reconstruction_error(x)
        if self.threshold <= 0:
            return np.zeros_like(errors)
        return np.clip(errors / self.threshold, 0.0, 2.0) / 2.0

    def save(self, path: Path, threshold: float):
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "threshold": threshold, "input_dim": self.input_dim}, path)

    @staticmethod
    def load(path: Path, input_dim: int):
        payload = joblib.load(path)
        obj = AutoencoderModel(input_dim=input_dim)
        obj.model = payload["model"]
        obj.threshold = float(payload.get("threshold", 0.0))
        return obj
