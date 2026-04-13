from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.ensemble import IsolationForest

MODEL_PATH = Path("model") / "isolation_forest.pkl"


def train_and_save() -> None:
    rng = np.random.default_rng(42)

    # Features: packet_rate, latency, error_rate, throughput, active_connections
    normal_data = np.column_stack(
        [
            rng.normal(loc=1200, scale=180, size=1200),
            rng.normal(loc=35, scale=7, size=1200),
            rng.normal(loc=0.02, scale=0.01, size=1200),
            rng.normal(loc=850, scale=120, size=1200),
            rng.normal(loc=220, scale=35, size=1200),
        ]
    )

    model = IsolationForest(contamination=0.08, random_state=42)
    model.fit(normal_data)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    dump(model, MODEL_PATH)
    print(f"Model saved: {MODEL_PATH.resolve()}")


if __name__ == "__main__":
    train_and_save()
