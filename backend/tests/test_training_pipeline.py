from app.ml.training import ModelTrainer


def test_training_outputs_artifacts(tmp_path, monkeypatch):
    trainer = ModelTrainer()
    trainer.artifacts_dir = tmp_path
    trainer.scaler_path = tmp_path / "scaler.joblib"
    trainer.iso_path = tmp_path / "isolation_forest.joblib"
    trainer.ae_path = tmp_path / "autoencoder.joblib"
    trainer.meta_path = tmp_path / "metadata.json"

    result = trainer.train(samples=1200, epochs=5)
    for path in result["artifacts"]:
        assert path
