from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    traffic_log_id: Mapped[int] = mapped_column(ForeignKey("traffic_logs.id", ondelete="CASCADE"), index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    traffic_log = relationship("TrafficLog", back_populates="anomaly_results")
    alerts = relationship("Alert", back_populates="anomaly_result", lazy="selectin")


Index("ix_anomaly_model_ts", AnomalyResult.model_name, AnomalyResult.detected_at)
