from datetime import datetime, timezone

from scapy.all import IP, TCP, UDP, rdpcap


def parse_pcap(file_path: str, limit: int = 1000) -> list[dict]:
    packets = rdpcap(file_path, count=limit)
    parsed: list[dict] = []

    prev_ts = None
    for pkt in packets:
        if IP not in pkt:
            continue

        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        protocol = "TCP" if TCP in pkt else "UDP" if UDP in pkt else "ICMP"
        packet_size = float(len(pkt))

        ts = datetime.fromtimestamp(float(pkt.time), tz=timezone.utc)
        if prev_ts is None:
            interval_ms = 30.0
        else:
            interval_ms = max(1.0, (ts - prev_ts).total_seconds() * 1000)
        prev_ts = ts

        request_frequency = max(1.0, 1000.0 / interval_ms)

        parsed.append(
            {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "packet_size": packet_size,
                "interval_ms": interval_ms,
                "request_frequency": request_frequency,
                "timestamp": ts,
            }
        )

    return parsed
