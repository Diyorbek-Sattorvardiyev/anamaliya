from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    src_ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    dst_ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    packet_size: Mapped[float] = mapped_column(Float, nullable=False)
    interval_ms: Mapped[float] = mapped_column(Float, nullable=False)
    request_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    anomaly_results = relationship("AnomalyResult", back_populates="traffic_log", lazy="selectin")


Index("ix_traffic_src_ts", TrafficLog.src_ip, TrafficLog.timestamp)
Index("ix_traffic_dst_ts", TrafficLog.dst_ip, TrafficLog.timestamp)
