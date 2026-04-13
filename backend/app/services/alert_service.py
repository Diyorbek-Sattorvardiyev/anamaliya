from sqlalchemy.orm import Session

from app.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, db: Session):
        self.alerts = AlertRepository(db)

    def create_alert(self, anomaly_result_id: int, message: str, severity: str = "high", channel: str = "web", user_id: int | None = None):
        return self.alerts.add_alert(
            anomaly_result_id=anomaly_result_id,
            user_id=user_id,
            severity=severity,
            channel=channel,
            message=message,
            status="triggered",
        )

    def list_alerts(self, limit: int = 200):
        return self.alerts.list_recent(limit=limit)
