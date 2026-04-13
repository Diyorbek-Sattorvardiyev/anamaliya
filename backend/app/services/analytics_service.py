from sqlalchemy.orm import Session

from app.repositories.anomaly_repository import AnomalyRepository
from app.repositories.traffic_repository import TrafficRepository


class AnalyticsService:
    def __init__(self, db: Session):
        self.traffic_repo = TrafficRepository(db)
        self.anomaly_repo = AnomalyRepository(db)

    def live_snapshot(self) -> dict:
        recent = self.traffic_repo.recent_points(minutes=30, limit=200)
        points = [
            {
                "timestamp": log.timestamp,
                "packet_size": log.packet_size,
                "request_frequency": log.request_frequency,
                "anomaly_score": anomaly.anomaly_score,
                "is_anomaly": anomaly.is_anomaly,
            }
            for log, anomaly in recent
        ]
        points.reverse()

        top_ips = [
            {"src_ip": src_ip, "anomaly_count": anomaly_count}
            for src_ip, anomaly_count in self.traffic_repo.top_suspicious_ips(limit=5)
        ]

        protocol_distribution = self.traffic_repo.protocol_distribution()

        total_anomalies = sum(1 for p in points if p["is_anomaly"])

        return {
            "points": points,
            "top_suspicious_ips": top_ips,
            "protocol_distribution": protocol_distribution,
            "total_anomalies": total_anomalies,
        }

    def anomalies(self, limit: int = 200):
        return self.anomaly_repo.list_recent(limit=limit)
