from datetime import datetime

from pydantic import BaseModel


class AlertRead(BaseModel):
    id: int
    anomaly_result_id: int
    severity: str
    channel: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
