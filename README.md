# F1 25 UDP Telemetry Python Package

A robust, high-performance Python package to ingest, parse, and process real-time UDP telemetry output broadcasted by the **F1® 25 Game**.

This library uses Python's `ctypes` module to memory-map the binary data sent over UDP by the F1 25 game into fully structured Python objects directly—resulting in zero-copy speed and an exact mapping to the official F1 specifications.

## Installation

Since this package is built securely onto standard Python features like socket and `ctypes`, it has **no external dependencies**.

You can install it directly from the source directory using `pip`:

```bash
# To install globally or within your virtual environment:
pip install .

# For developers wanting changes to apply without reinstalling:
pip install -e .
```

## Quick Start Guide

The easiest way to process telemetry data is to configure the `TelemetryListener` iterator that automatically unpacks UDP payloads and yields the matching structure.

### Basic Application Example

```python
from f1GameTelemetry.listener import TelemetryListener
from f1GameTelemetry.packets import PacketLapData, PacketCarTelemetryData
import time

# Create listener bound to default local IP and telemetry port
listener = TelemetryListener(host="127.0.0.1", port=20777)

print("Starting telemetry listener on UDP port 20777...")
print("Waiting for F1 25 data...")

try:
    for packet in listener.get():
        
        # Example 1: Read the Lap Data packet specifically
        if isinstance(packet, PacketLapData):
            # Access the player's car
            player_index = packet.m_header.m_playerCarIndex
            lap_data = packet.m_lapData[player_index]
            print(f"Current Lap Time (ms): {lap_data.m_currentLapTimeInMS}")
            
        # Example 2: Access live car telemetry
        if isinstance(packet, PacketCarTelemetryData):
            player_index = packet.m_header.m_playerCarIndex
            telemetry = packet.m_carTelemetryData[player_index]
            
            # Print Speed, Throttle, and Brake cleanly
            print(f"Speed: {telemetry.m_speed} km/h | Throttle: {telemetry.m_throttle:.2f} | Brake: {telemetry.m_brake:.2f}")

except KeyboardInterrupt:
    print("\nTelemetry closed.")
    listener.close()
```

### JSON Serialization & Exporting

If you immediately want to serialize these instances down to JSON strings to use over a WebSocket array or store dynamically, the objects come with a useful `to_dict()` recursive serializer!

```python
import json
from f1GameTelemetry.listener import TelemetryListener

for packet in TelemetryListener().get():
    # Convert ctypes Packet down to nested raw primitives automatically
    packet_data = packet.to_dict()
    print(json.dumps(packet_data, indent=2))
```

## Configuration In F1 25 Menu

To utilize this package with real simulation data, you must activate telemetry in the Formula 1 menus!

1. Open **F1 25** and go to `Game Options -> Settings -> UDP Telemetry Settings`.
2. Toggle **UDP Telemetry** ON.
3. Keep the format version set to `2025` (Default).
4. Verify your IP is set correctly—if you play on PC on the same machine the python script runs on, it should be `127.0.0.1`.
5. Verify the listening port is set to `20777` (Default)
6. Choose a sensible output rate (e.g. `20Hz` or `60Hz`).

## Important Constants & Enums

All IDs presented within the data streams can be decoded securely using `f1GameTelemetry.constants`.

```python
from f1GameTelemetry.constants import TEAM_IDS, DRIVER_IDS, TRACK_IDS

driver_name = DRIVER_IDS.get(9)
print(f"Driver ID 9 belongs to: {driver_name}") # Max Verstappen!
```
