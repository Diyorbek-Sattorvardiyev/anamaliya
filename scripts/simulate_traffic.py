"""Generate normal and DDoS-like traffic and send it to the API."""

import random
from datetime import datetime, timezone

import requests

API = "http://localhost:8000/api/v1"
EMAIL = "admin@netsentinel.local"
PASSWORD = "Admin12345"


def login_token() -> str:
    res = requests.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    res.raise_for_status()
    return res.json()["access_token"]


def make_packet(ddos: bool) -> dict:
    if ddos:
        return {
            "src_ip": random.choice(["203.0.113.5", "198.51.100.8", "192.0.2.15"]),
            "dst_ip": "10.0.0.1",
            "protocol": random.choice(["TCP", "UDP", "ICMP"]),
            "packet_size": random.uniform(1200, 2200),
            "interval_ms": random.uniform(0.8, 6.0),
            "request_frequency": random.uniform(250, 1800),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "src_ip": random.choice(["10.0.0.10", "10.0.0.20", "172.16.0.11"]),
        "dst_ip": random.choice(["10.0.0.1", "10.0.0.2"]),
        "protocol": random.choice(["TCP", "UDP", "HTTP", "HTTPS"]),
        "packet_size": random.uniform(250, 1200),
        "interval_ms": random.uniform(8, 90),
        "request_frequency": random.uniform(10, 90),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    token = login_token()
    headers = {"Authorization": f"Bearer {token}"}

    packets = [make_packet(ddos=False) for _ in range(80)] + [make_packet(ddos=True) for _ in range(50)]
    random.shuffle(packets)

    resp = requests.post(
        f"{API}/traffic/ingest",
        json={"packets": packets, "simulate_count": 0, "async_mode": False},
        headers=headers,
        timeout=20,
    )
    resp.raise_for_status()
    print(resp.json())


if __name__ == "__main__":
    main()
