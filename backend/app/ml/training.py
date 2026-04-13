import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

from app.core.config import get_settings
from app.ml.autoencoder import AutoencoderModel
from app.ml.features import FEATURE_COLUMNS, generate_synthetic_packets, packet_to_feature_dict, to_dataframe
from app.ml.iso_forest import IsolationForestModel


class ModelTrainer:
    def __init__(self):
        settings = get_settings()
        self.artifacts_dir = Path(settings.model_artifact_dir)
        self.scaler_path = self.artifacts_dir / "scaler.joblib"
        self.iso_path = self.artifacts_dir / "isolation_forest.joblib"
        self.ae_path = self.artifacts_dir / "autoencoder.joblib"
        self.meta_path = self.artifacts_dir / "metadata.json"

    def train(self, samples: int = 5000, epochs: int = 20) -> dict:
        packets = generate_synthetic_packets(samples=samples)
        labels = np.array([p["label"] for p in packets], dtype=int)

        feature_rows = [packet_to_feature_dict(p) for p in packets]
        df = to_dataframe(feature_rows)
        x = df[FEATURE_COLUMNS].values

        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        normal_x = x_scaled[labels == 0]

        iso = IsolationForestModel(contamination=0.12)
        iso.fit(normal_x)
        iso.save(self.iso_path)

        ae = AutoencoderModel(input_dim=normal_x.shape[1])
        ae.fit(normal_x, epochs=epochs)
        ae.save(self.ae_path, threshold=ae.threshold)

        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(scaler, self.scaler_path)

        metadata = {
            "feature_columns": FEATURE_COLUMNS,
            "autoencoder_threshold": ae.threshold,
            "trained_samples": samples,
            "epochs": epochs,
        }
        self.meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return {
            "artifacts": [str(self.scaler_path), str(self.iso_path), str(self.ae_path), str(self.meta_path)],
            "threshold": ae.threshold,
        }
