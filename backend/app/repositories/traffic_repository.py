from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models import AnomalyResult, TrafficLog


class TrafficRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_log(self, **kwargs) -> TrafficLog:
        log = TrafficLog(**kwargs)
        self.db.add(log)
        self.db.flush()
        return log

    def recent_points(self, minutes: int = 30, limit: int = 200):
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return (
            self.db.query(TrafficLog, AnomalyResult)
            .join(AnomalyResult, AnomalyResult.traffic_log_id == TrafficLog.id)
            .filter(TrafficLog.timestamp >= since)
            .order_by(desc(TrafficLog.timestamp))
            .limit(limit)
            .all()
        )

    def top_suspicious_ips(self, limit: int = 5):
        return (
            self.db.query(TrafficLog.src_ip, func.count(AnomalyResult.id).label("anomaly_count"))
            .join(AnomalyResult, AnomalyResult.traffic_log_id == TrafficLog.id)
            .filter(AnomalyResult.is_anomaly.is_(True))
            .group_by(TrafficLog.src_ip)
            .order_by(desc("anomaly_count"))
            .limit(limit)
            .all()
        )

    def protocol_distribution(self):
        rows = self.db.query(TrafficLog.protocol, func.count(TrafficLog.id)).group_by(TrafficLog.protocol).all()
        return {protocol: count for protocol, count in rows}
