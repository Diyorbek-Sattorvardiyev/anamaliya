from app.ml.features import packet_to_feature_dict


def test_packet_to_feature_dict_has_expected_fields():
    packet = {
        "src_ip": "10.0.0.10",
        "dst_ip": "10.0.0.1",
        "protocol": "TCP",
        "packet_size": 900,
        "interval_ms": 30,
        "request_frequency": 50,
    }
    features = packet_to_feature_dict(packet)

    assert "packet_size" in features
    assert "bytes_per_second" in features
    assert features["protocol_num"] == 2.0
