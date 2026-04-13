import json
from pathlib import Path

import joblib
import numpy as np

from app.core.config import get_settings
from app.ml.autoencoder import AutoencoderModel
from app.ml.features import FEATURE_COLUMNS, packet_to_feature_dict, to_dataframe
from app.ml.iso_forest import IsolationForestModel
from app.ml.training import ModelTrainer


class ModelInferenceService:
    def __init__(self):
        settings = get_settings()
        self.artifacts_dir = Path(settings.model_artifact_dir)
        self.scaler_path = self.artifacts_dir / "scaler.joblib"
        self.iso_path = self.artifacts_dir / "isolation_forest.joblib"
        self.ae_path = self.artifacts_dir / "autoencoder.joblib"
        self.meta_path = self.artifacts_dir / "metadata.json"
        self.settings = settings
        self._load_or_bootstrap()

    def _load_or_bootstrap(self):
        if not (self.scaler_path.exists() and self.iso_path.exists() and self.ae_path.exists() and self.meta_path.exists()):
            ModelTrainer().train()

        self.scaler = joblib.load(self.scaler_path)
        metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        self.feature_columns = metadata.get("feature_columns", FEATURE_COLUMNS)

        self.iso_model = IsolationForestModel.load(self.iso_path)
        self.ae_model = AutoencoderModel.load(self.ae_path, input_dim=len(self.feature_columns))

    def score_packet(self, packet: dict) -> dict:
        row = packet_to_feature_dict(packet)
        df = to_dataframe([row])
        x = df[self.feature_columns].values
        x_scaled = self.scaler.transform(x)

        iso_score = float(self.iso_model.predict_score(x_scaled)[0])
        ae_score = float(self.ae_model.predict_score(x_scaled)[0])
        ensemble = (iso_score + ae_score) / 2.0
        is_anomaly = ensemble >= self.settings.anomaly_alert_threshold

        return {
            "ensemble_score": round(ensemble, 4),
            "isolation_forest_score": round(iso_score, 4),
            "autoencoder_score": round(ae_score, 4),
            "is_anomaly": bool(is_anomaly),
        }
