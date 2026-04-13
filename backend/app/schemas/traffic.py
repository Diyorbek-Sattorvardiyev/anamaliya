from datetime import datetime
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, Field

IPAddress = IPv4Address | IPv6Address


class PacketIngestItem(BaseModel):
    src_ip: IPAddress
    dst_ip: IPAddress
    protocol: str = Field(default="TCP", pattern="^(TCP|UDP|ICMP|HTTP|HTTPS)$")
    packet_size: float = Field(gt=0, le=100000)
    interval_ms: float = Field(gt=0, le=60000)
    request_frequency: float = Field(gt=0, le=100000)
    timestamp: datetime | None = None


class IngestRequest(BaseModel):
    packets: list[PacketIngestItem] = Field(default_factory=list)
    simulate_count: int = Field(default=0, ge=0, le=500)
    async_mode: bool = False


class IngestResponse(BaseModel):
    message: str
    processed: int
    task_id: str | None = None


class TrafficPoint(BaseModel):
    timestamp: datetime
    packet_size: float
    request_frequency: float
    anomaly_score: float
    is_anomaly: bool


class TopSuspiciousIP(BaseModel):
    src_ip: str
    anomaly_count: int


class TrafficLiveResponse(BaseModel):
    points: list[TrafficPoint]
    top_suspicious_ips: list[TopSuspiciousIP]
    protocol_distribution: dict[str, int]
    total_anomalies: int
