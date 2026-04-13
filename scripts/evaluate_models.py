"""Offline evaluation on synthetic normal + DDoS-like traffic."""

from app.ml.features import generate_synthetic_packets
from app.ml.inference import ModelInferenceService
from app.ml.training import ModelTrainer


def evaluate(samples: int = 6000) -> dict:
    trainer = ModelTrainer()
    trainer.train(samples=samples, epochs=20)

    packets = generate_synthetic_packets(samples=samples, anomalous_ratio=0.25)
    inference = ModelInferenceService()

    y_true = [p["label"] for p in packets]
    y_pred = [1 if inference.score_packet(p)["is_anomaly"] else 0 for p in packets]

    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    accuracy = (tp + tn) / max(1, len(y_true))
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)

    return {
        "samples": samples,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
    }


if __name__ == "__main__":
    print(evaluate())
