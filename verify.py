import ctypes
from f1GameTelemetry.packets import PacketSessionData, PacketHeader, PacketMotionData

tests = [
    ("Session", PacketSessionData, 753),
    ("Motion", PacketMotionData, 1349),
]

for name, pkt_class, expected_size in tests:
    actual = ctypes.sizeof(pkt_class)
    print(f"{name} Packet Size: {actual} bytes. Expected: {expected_size} bytes. Match: {actual == expected_size}")

