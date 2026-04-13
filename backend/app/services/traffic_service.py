from datetime import datetime, timezone

import numpy as np
from sqlalchemy.orm import Session

from app.ml.inference import ModelInferenceService
from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.traffic_repository import TrafficRepository
from app.services.alert_service import AlertService


class TrafficService:
    def __init__(self, db: Session):
        self.db = db
        self.traffic_repo = TrafficRepository(db)
        self.anomaly_repo = AnomalyRepository(db)
        self.alert_service = AlertService(db)
        self.inference = ModelInferenceService()

    @staticmethod
    def simulate_packets(count: int = 20) -> list[dict]:
        rng = np.random.default_rng()
        packets = []
        for _ in range(count):
            anomalous = rng.random() < 0.15
            packets.append(
                {
                    "src_ip": str(rng.choice(["10.0.0.10", "10.0.0.20", "172.16.0.11", "203.0.113.5"])),
                    "dst_ip": str(rng.choice(["10.0.0.1", "10.0.0.2", "10.0.0.3"])),
                    "protocol": str(rng.choice(["TCP", "UDP", "ICMP", "HTTP", "HTTPS"])),
                    "packet_size": float(rng.normal(1400, 200) if anomalous else rng.normal(700, 120)),
                    "interval_ms": float(max(1, rng.normal(3, 1.5) if anomalous else rng.normal(30, 10))),
                    "request_frequency": float(max(1, rng.normal(500, 120) if anomalous else rng.normal(50, 20))),
                    "timestamp": datetime.now(timezone.utc),
                }
            )
        return packets

    def process_packets(self, packets: list[dict]) -> int:
        processed = 0
        for packet in packets:
            ts = packet.get("timestamp") or datetime.now(timezone.utc)
            score = self.inference.score_packet(packet)

            log = self.traffic_repo.add_log(
                src_ip=str(packet["src_ip"]),
                dst_ip=str(packet["dst_ip"]),
                protocol=str(packet["protocol"]),
                packet_size=float(packet["packet_size"]),
                interval_ms=float(packet["interval_ms"]),
                request_frequency=float(packet["request_frequency"]),
                timestamp=ts,
            )

            anomaly_result = self.anomaly_repo.add_result(
                traffic_log_id=log.id,
                model_name="ensemble(isolation_forest+autoencoder)",
                anomaly_score=score["ensemble_score"],
                is_anomaly=score["is_anomaly"],
            )

            if score["is_anomaly"]:
                self.alert_service.create_alert(
                    anomaly_result_id=anomaly_result.id,
                    message=(
                        f"Anomaly detected from {packet['src_ip']} -> {packet['dst_ip']} "
                        f"(score={score['ensemble_score']})"
                    ),
                    severity="high" if score["ensemble_score"] > 0.9 else "medium",
                    channel="web",
                )
                # Fire-and-forget email alert via Celery worker.
                try:
                    from app.workers.tasks import send_email_notification

                    send_email_notification.delay(
                        "admin@netsentinel.local",
                        "NetSentinel anomaly alert",
                        (
                            f"Potential anomaly detected from {packet['src_ip']} "
                            f"to {packet['dst_ip']} with score {score['ensemble_score']}"
                        ),
                    )
                except Exception:
                    # Keep ingestion resilient even if queue/email is temporarily unavailable.
                    pass

            processed += 1

        self.db.commit()
        return processed
