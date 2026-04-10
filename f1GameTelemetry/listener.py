import socket
import ctypes
import logging
from . import packets

logger = logging.getLogger(__name__)

PACKET_ID_MAP = {
    0: packets.PacketMotionData,
    1: packets.PacketSessionData,
    2: packets.PacketLapData,
    3: packets.PacketEventData,
    4: packets.PacketParticipantsData,
    5: packets.PacketCarSetupData,
    6: packets.PacketCarTelemetryData,
    7: packets.PacketCarStatusData,
    8: packets.PacketFinalClassificationData,
    9: packets.PacketLobbyInfoData,
    10: packets.PacketCarDamageData,
    11: packets.PacketSessionHistoryData,
    12: packets.PacketTyreSetsData,
    13: packets.PacketMotionExData,
    14: packets.PacketTimeTrialData,
    15: packets.PacketLapPositionsData,
}

class TelemetryListener:
    def __init__(self, host="127.0.0.1", port=20777):
        """
        Creates a UDP listener for F1 25 telemetry.
        """
        self.host = host
        self.port = port
        self.socket = None

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allows multiple processes to listen to the same port if needed
        try:
            # Unix
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        
        self.socket.bind((self.host, self.port))
        logger.info(f"Listening for F1 25 telemetry on UDP {self.host}:{self.port}")

    def close(self):
        if self.socket:
            self.socket.close()

    def get(self):
        """
        Generator that yields unpacked python objects representing telemetry packets.
        """
        if not self.socket:
            self.start()
            
        while True:
            try:
                data, addr = self.socket.recvfrom(2048) # Buffer size needs to be larger than largest packet (1460 bytes)
                
                # Check header first to determine packet type
                if len(data) < ctypes.sizeof(packets.PacketHeader):
                    logger.warning("Received data too small for a packet header.")
                    continue
                    
                header = packets.PacketHeader.from_buffer_copy(data)
                
                if header.m_packetFormat != 2025:
                    logger.warning(f"Received packet with unsupported format: {header.m_packetFormat}. Expected 2025.")
                    
                packet_class = PACKET_ID_MAP.get(header.m_packetId)
                if not packet_class:
                    logger.warning(f"Unknown packet ID received: {header.m_packetId}")
                    continue
                    
                if len(data) != ctypes.sizeof(packet_class):
                    # F1 sometimes sends short packets if e.g. lobby is not full
                    # We can use ctypes.memmove to a zero-initialized buffer
                    # or just allow a truncation if it's smaller, though ctypes expects exact or larger.
                    buffer = bytearray(ctypes.sizeof(packet_class))
                    copy_len = min(len(data), len(buffer))
                    buffer[:copy_len] = data[:copy_len]
                    packet = packet_class.from_buffer_copy(buffer)
                else:
                    packet = packet_class.from_buffer_copy(data)
                    
                yield packet
                
            except socket.error as e:
                logger.error(f"Socket error: {e}")
                break
