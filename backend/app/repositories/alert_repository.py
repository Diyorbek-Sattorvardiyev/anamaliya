from sqlalchemy.orm import Session

from app.db.models import Alert


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_alert(self, **kwargs) -> Alert:
        row = Alert(**kwargs)
        self.db.add(row)
        self.db.flush()
        return row

    def list_recent(self, limit: int = 200) -> list[Alert]:
        return self.db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()
