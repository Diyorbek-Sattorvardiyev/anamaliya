from sqlalchemy.orm import Session

from app.db.models import AnomalyResult


class AnomalyRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_result(self, **kwargs) -> AnomalyResult:
        row = AnomalyResult(**kwargs)
        self.db.add(row)
        self.db.flush()
        return row

    def list_recent(self, limit: int = 200) -> list[AnomalyResult]:
        return self.db.query(AnomalyResult).order_by(AnomalyResult.detected_at.desc()).limit(limit).all()
