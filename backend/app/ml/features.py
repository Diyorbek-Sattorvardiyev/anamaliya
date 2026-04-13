from datetime import datetime, timezone

import numpy as np
import pandas as pd

PROTOCOL_MAP = {"ICMP": 1.0, "TCP": 2.0, "UDP": 3.0, "HTTP": 4.0, "HTTPS": 5.0}
FEATURE_COLUMNS = [
    "packet_size",
    "interval_ms",
    "request_frequency",
    "bytes_per_second",
    "protocol_num",
    "hour_sin",
    "hour_cos",
]


def packet_to_feature_dict(packet: dict) -> dict:
    ts = packet.get("timestamp") or datetime.now(timezone.utc)
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    hour = ts.hour + (ts.minute / 60)

    interval_ms = max(float(packet["interval_ms"]), 1.0)
    packet_size = float(packet["packet_size"])

    return {
        "packet_size": packet_size,
        "interval_ms": interval_ms,
        "request_frequency": float(packet["request_frequency"]),
        "bytes_per_second": packet_size / (interval_ms / 1000.0),
        "protocol_num": PROTOCOL_MAP.get(packet["protocol"], 0.0),
        "hour_sin": float(np.sin(2 * np.pi * hour / 24.0)),
        "hour_cos": float(np.cos(2 * np.pi * hour / 24.0)),
    }


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)


def generate_synthetic_packets(samples: int = 5000, anomalous_ratio: float = 0.15) -> list[dict]:
    rng = np.random.default_rng(42)
    packets: list[dict] = []

    normal_n = int(samples * (1 - anomalous_ratio))
    anomaly_n = samples - normal_n

    for _ in range(normal_n):
        packets.append(
            {
                "src_ip": "10.0.0.10",
                "dst_ip": "10.0.0.1",
                "protocol": rng.choice(["TCP", "UDP", "HTTP", "HTTPS"], p=[0.35, 0.25, 0.20, 0.20]),
                "packet_size": float(np.clip(rng.normal(700, 160), 64, 1600)),
                "interval_ms": float(np.clip(rng.normal(30, 12), 1, 300)),
                "request_frequency": float(np.clip(rng.normal(45, 15), 1, 300)),
                "timestamp": datetime.now(timezone.utc),
                "label": 0,
            }
        )

    for _ in range(anomaly_n):
        packets.append(
            {
                "src_ip": "203.0.113.5",
                "dst_ip": "10.0.0.1",
                "protocol": rng.choice(["TCP", "UDP", "ICMP"], p=[0.5, 0.35, 0.15]),
                "packet_size": float(np.clip(rng.normal(1400, 280), 128, 9000)),
                "interval_ms": float(np.clip(rng.normal(3, 2), 0.5, 30)),
                "request_frequency": float(np.clip(rng.normal(450, 140), 50, 3000)),
                "timestamp": datetime.now(timezone.utc),
                "label": 1,
            }
        )

    rng.shuffle(packets)
    return packets
