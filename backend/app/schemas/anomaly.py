from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnomalyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: int
    traffic_log_id: int
    model_name: str
    anomaly_score: float
    is_anomaly: bool
    detected_at: datetime
