import re
import sys

raw_text = """
struct PacketHeader
{
    uint16    m_packetFormat;             // 2025
    uint8     m_gameYear;                 // Game year - last two digits e.g. 25
    uint8     m_gameMajorVersion;         // Game major version - "X.00"
    uint8     m_gameMinorVersion;         // Game minor version - "1.XX"
    uint8     m_packetVersion;            // Version of this packet type, all start from 1
    uint8     m_packetId;                 // Identifier for the packet type, see below
    uint64    m_sessionUID;               // Unique identifier for the session
    float     m_sessionTime;              // Session timestamp
    uint32    m_frameIdentifier;          // Identifier for the frame the data was retrieved on
    uint32    m_overallFrameIdentifier;   // Overall identifier for the frame the data was retrieved
                                          // on, doesn't go back after flashbacks
    uint8     m_playerCarIndex;           // Index of player's car in the array
    uint8     m_secondaryPlayerCarIndex;  // Index of secondary player's car in the array (splitscreen)
                                          // 255 if no second player
};

struct CarMotionData {
    float m_worldPositionX;
    float m_worldPositionY;
    float m_worldPositionZ;
    float m_worldVelocityX;
    float m_worldVelocityY;
    float m_worldVelocityZ;
    int16 m_worldForwardDirX;
    int16 m_worldForwardDirY;
    int16 m_worldForwardDirZ;
    int16 m_worldRightDirX;
    int16 m_worldRightDirY;
    int16 m_worldRightDirZ;
    float m_gForceLateral;
    float m_gForceLongitudinal;
    float m_gForceVertical;
    float m_yaw;
    float m_pitch;
    float m_roll;
};

struct PacketMotionData {
    PacketHeader m_header;
    CarMotionData m_carMotionData[22];
};

struct MarshalZone {
    float m_zoneStart;
    int8 m_zoneFlag;
};

struct WeatherForecastSample {
    uint8 m_sessionType;
    uint8 m_timeOffset;
    uint8 m_weather;
    int8 m_trackTemperature;
    int8 m_trackTemperatureChange;
    int8 m_airTemperature;
    int8 m_airTemperatureChange;
    uint8 m_rainPercentage;
};

struct PacketSessionData {
    PacketHeader m_header;
    uint8 m_weather;
    int8 m_trackTemperature;
    int8 m_airTemperature;
    uint8 m_totalLaps;
    uint16 m_trackLength;
    uint8 m_sessionType;
    int8 m_trackId;
    uint8 m_formula;
    uint16 m_sessionTimeLeft;
    uint16 m_sessionDuration;
    uint8 m_pitSpeedLimit;
    uint8 m_gamePaused;
    uint8 m_isSpectating;
    uint8 m_spectatorCarIndex;
    uint8 m_sliProNativeSupport;
    uint8 m_numMarshalZones;
    MarshalZone m_marshalZones[21];
    uint8 m_safetyCarStatus;
    uint8 m_networkGame;
    uint8 m_numWeatherForecastSamples;
    WeatherForecastSample m_weatherForecastSamples[64];
    uint8 m_forecastAccuracy;
    uint8 m_aiDifficulty;
    uint32 m_seasonLinkIdentifier;
    uint32 m_weekendLinkIdentifier;
    uint32 m_sessionLinkIdentifier;
    uint8 m_pitStopWindowIdealLap;
    uint8 m_pitStopWindowLatestLap;
    uint8 m_pitStopRejoinPosition;
    uint8 m_steeringAssist;
    uint8 m_brakingAssist;
    uint8 m_gearboxAssist;
    uint8 m_pitAssist;
    uint8 m_pitReleaseAssist;
    uint8 m_ERSAssist;
    uint8 m_DRSAssist;
    uint8 m_dynamicRacingLine;
    uint8 m_dynamicRacingLineType;
    uint8 m_gameMode;
    uint8 m_ruleSet;
    uint32 m_timeOfDay;
    uint8 m_sessionLength;
    uint8 m_speedUnitsLeadPlayer;
    uint8 m_temperatureUnitsLeadPlayer;
    uint8 m_speedUnitsSecondaryPlayer;
    uint8 m_temperatureUnitsSecondaryPlayer;
    uint8 m_numSafetyCarPeriods;
    uint8 m_numVirtualSafetyCarPeriods;
    uint8 m_numRedFlagPeriods;
    uint8 m_equalCarPerformance;
    uint8 m_recoveryMode;
    uint8 m_flashbackLimit;
    uint8 m_surfaceType;
    uint8 m_lowFuelMode;
    uint8 m_raceStarts;
    uint8 m_tyreTemperature;
    uint8 m_pitLaneTyreSim;
    uint8 m_carDamage;
    uint8 m_carDamageRate;
    uint8 m_collisions;
    uint8 m_collisionsOffForFirstLapOnly;
    uint8 m_mpUnsafePitRelease;
    uint8 m_mpOffForGriefing;
    uint8 m_cornerCuttingStringency;
    uint8 m_parcFermeRules;
    uint8 m_pitStopExperience;
    uint8 m_safetyCar;
    uint8 m_safetyCarExperience;
    uint8 m_formationLap;
    uint8 m_formationLapExperience;
    uint8 m_redFlags;
    uint8 m_affectsLicenceLevelSolo;
    uint8 m_affectsLicenceLevelMP;
    uint8 m_numSessionsInWeekend;
    uint8 m_weekendStructure[12];
    float m_sector2LapDistanceStart;
    float m_sector3LapDistanceStart;
};

struct LapData {
    uint32 m_lastLapTimeInMS;
    uint32 m_currentLapTimeInMS;
    uint16 m_sector1TimeMSPart;
    uint8 m_sector1TimeMinutesPart;
    uint16 m_sector2TimeMSPart;
    uint8 m_sector2TimeMinutesPart;
    uint16 m_deltaToCarInFrontMSPart;
    uint8 m_deltaToCarInFrontMinutesPart;
    uint16 m_deltaToRaceLeaderMSPart;
    uint8 m_deltaToRaceLeaderMinutesPart;
    float m_lapDistance;
    float m_totalDistance;
    float m_safetyCarDelta;
    uint8 m_carPosition;
    uint8 m_currentLapNum;
    uint8 m_pitStatus;
    uint8 m_numPitStops;
    uint8 m_sector;
    uint8 m_currentLapInvalid;
    uint8 m_penalties;
    uint8 m_totalWarnings;
    uint8 m_cornerCuttingWarnings;
    uint8 m_numUnservedDriveThroughPens;
    uint8 m_numUnservedStopGoPens;
    uint8 m_gridPosition;
    uint8 m_driverStatus;
    uint8 m_resultStatus;
    uint8 m_pitLaneTimerActive;
    uint16 m_pitLaneTimeInLaneInMS;
    uint16 m_pitStopTimerInMS;
    uint8 m_pitStopShouldServePen;
    float m_speedTrapFastestSpeed;
    uint8 m_speedTrapFastestLap;
};

struct PacketLapData {
    PacketHeader m_header;
    LapData m_lapData[22];
    uint8 m_timeTrialPBCarIdx;
    uint8 m_timeTrialRivalCarIdx;
};

struct ParticipantData {
    uint8 m_aiControlled;
    uint8 m_driverId;
    uint8 m_networkId;
    uint8 m_teamId;
    uint8 m_myTeam;
    uint8 m_raceNumber;
    uint8 m_nationality;
    char m_name[32];
    uint8 m_yourTelemetry;
    uint8 m_showOnlineNames;
    uint16 m_techLevel;
    uint8 m_platform;
    uint8 m_numColours;
    uint8 m_liveryColours[12]; // LiveryColour is 3 bytes, up to 4 = 12
};

struct PacketParticipantsData {
    PacketHeader m_header;
    uint8 m_numActiveCars;
    ParticipantData m_participants[22];
};

struct CarSetupData {
    uint8 m_frontWing;
    uint8 m_rearWing;
    uint8 m_onThrottle;
    uint8 m_offThrottle;
    float m_frontCamber;
    float m_rearCamber;
    float m_frontToe;
    float m_rearToe;
    uint8 m_frontSuspension;
    uint8 m_rearSuspension;
    uint8 m_frontAntiRollBar;
    uint8 m_rearAntiRollBar;
    uint8 m_frontSuspensionHeight;
    uint8 m_rearSuspensionHeight;
    uint8 m_brakePressure;
    uint8 m_brakeBias;
    uint8 m_engineBraking;
    float m_rearLeftTyrePressure;
    float m_rearRightTyrePressure;
    float m_frontLeftTyrePressure;
    float m_frontRightTyrePressure;
    uint8 m_ballast;
    float m_fuelLoad;
};

struct PacketCarSetupData {
    PacketHeader m_header;
    CarSetupData m_carSetups[22];
    float m_nextFrontWingValue;
};

struct CarTelemetryData {
    uint16 m_speed;
    float m_throttle;
    float m_steer;
    float m_brake;
    uint8 m_clutch;
    int8 m_gear;
    uint16 m_engineRPM;
    uint8 m_drs;
    uint8 m_revLightsPercent;
    uint16 m_revLightsBitValue;
    uint16 m_brakesTemperature[4];
    uint8 m_tyresSurfaceTemperature[4];
    uint8 m_tyresInnerTemperature[4];
    uint16 m_engineTemperature;
    float m_tyresPressure[4];
    uint8 m_surfaceType[4];
};

struct PacketCarTelemetryData {
    PacketHeader m_header;
    CarTelemetryData m_carTelemetryData[22];
    uint8 m_mfdPanelIndex;
    uint8 m_mfdPanelIndexSecondaryPlayer;
    int8 m_suggestedGear;
};

struct CarStatusData {
    uint8 m_tractionControl;
    uint8 m_antiLockBrakes;
    uint8 m_fuelMix;
    uint8 m_frontBrakeBias;
    uint8 m_pitLimiterStatus;
    float m_fuelInTank;
    float m_fuelCapacity;
    float m_fuelRemainingLaps;
    uint16 m_maxRPM;
    uint16 m_idleRPM;
    uint8 m_maxGears;
    uint8 m_drsAllowed;
    uint16 m_drsActivationDistance;
    uint8 m_actualTyreCompound;
    uint8 m_visualTyreCompound;
    uint8 m_tyresAgeLaps;
    int8 m_vehicleFiaFlags;
    float m_enginePowerICE;
    float m_enginePowerMGUK;
    float m_ersStoreEnergy;
    uint8 m_ersDeployMode;
    float m_ersHarvestedThisLapMGUK;
    float m_ersHarvestedThisLapMGUH;
    float m_ersDeployedThisLap;
    uint8 m_networkPaused;
};

struct PacketCarStatusData {
    PacketHeader m_header;
    CarStatusData m_carStatusData[22];
};

struct FinalClassificationData {
    uint8 m_position;
    uint8 m_numLaps;
    uint8 m_gridPosition;
    uint8 m_points;
    uint8 m_numPitStops;
    uint8 m_resultStatus;
    uint8 m_resultReason;
    uint32 m_bestLapTimeInMS;
    double m_totalRaceTime;
    uint8 m_penaltiesTime;
    uint8 m_numPenalties;
    uint8 m_numTyreStints;
    uint8 m_tyreStintsActual[8];
    uint8 m_tyreStintsVisual[8];
    uint8 m_tyreStintsEndLaps[8];
};

struct PacketFinalClassificationData {
    PacketHeader m_header;
    uint8 m_numCars;
    FinalClassificationData m_classificationData[22];
};

struct LobbyInfoData {
    uint8 m_aiControlled;
    uint8 m_teamId;
    uint8 m_nationality;
    uint8 m_platform;
    char m_name[32];
    uint8 m_carNumber;
    uint8 m_yourTelemetry;
    uint8 m_showOnlineNames;
    uint16 m_techLevel;
    uint8 m_readyStatus;
};

struct PacketLobbyInfoData {
    PacketHeader m_header;
    uint8 m_numPlayers;
    LobbyInfoData m_lobbyPlayers[22];
};

struct CarDamageData {
    float m_tyresWear[4];
    uint8 m_tyresDamage[4];
    uint8 m_brakesDamage[4];
    uint8 m_tyreBlisters[4];
    uint8 m_frontLeftWingDamage;
    uint8 m_frontRightWingDamage;
    uint8 m_rearWingDamage;
    uint8 m_floorDamage;
    uint8 m_diffuserDamage;
    uint8 m_sidepodDamage;
    uint8 m_drsFault;
    uint8 m_ersFault;
    uint8 m_gearBoxDamage;
    uint8 m_engineDamage;
    uint8 m_engineMGUHWear;
    uint8 m_engineESWear;
    uint8 m_engineCEWear;
    uint8 m_engineICEWear;
    uint8 m_engineMGUKWear;
    uint8 m_engineTCWear;
    uint8 m_engineBlown;
    uint8 m_engineSeized;
};

struct PacketCarDamageData {
    PacketHeader m_header;
    CarDamageData m_carDamageData[22];
};

struct LapHistoryData {
    uint32 m_lapTimeInMS;
    uint16 m_sector1TimeMSPart;
    uint8 m_sector1TimeMinutesPart;
    uint16 m_sector2TimeMSPart;
    uint8 m_sector2TimeMinutesPart;
    uint16 m_sector3TimeMSPart;
    uint8 m_sector3TimeMinutesPart;
    uint8 m_lapValidBitFlags;
};

struct TyreStintHistoryData {
    uint8 m_endLap;
    uint8 m_tyreActualCompound;
    uint8 m_tyreVisualCompound;
};

struct PacketSessionHistoryData {
    PacketHeader m_header;
    uint8 m_carIdx;
    uint8 m_numLaps;
    uint8 m_numTyreStints;
    uint8 m_bestLapTimeLapNum;
    uint8 m_bestSector1LapNum;
    uint8 m_bestSector2LapNum;
    uint8 m_bestSector3LapNum;
    LapHistoryData m_lapHistoryData[100];
    TyreStintHistoryData m_tyreStintsHistoryData[8];
};

struct TyreSetData {
    uint8 m_actualTyreCompound;
    uint8 m_visualTyreCompound;
    uint8 m_wear;
    uint8 m_available;
    uint8 m_recommendedSession;
    uint8 m_lifeSpan;
    uint8 m_usableLife;
    int16 m_lapDeltaTime;
    uint8 m_fitted;
};

struct PacketTyreSetsData {
    PacketHeader m_header;
    uint8 m_carIdx;
    TyreSetData m_tyreSetData[20];
    uint8 m_fittedIdx;
};

struct PacketMotionExData {
    PacketHeader m_header;
    float m_suspensionPosition[4];
    float m_suspensionVelocity[4];
    float m_suspensionAcceleration[4];
    float m_wheelSpeed[4];
    float m_wheelSlipRatio[4];
    float m_wheelSlipAngle[4];
    float m_wheelLatForce[4];
    float m_wheelLongForce[4];
    float m_heightOfCOGAboveGround;
    float m_localVelocityX;
    float m_localVelocityY;
    float m_localVelocityZ;
    float m_angularVelocityX;
    float m_angularVelocityY;
    float m_angularVelocityZ;
    float m_angularAccelerationX;
    float m_angularAccelerationY;
    float m_angularAccelerationZ;
    float m_frontWheelsAngle;
    float m_wheelVertForce[4];
    float m_frontAeroHeight;
    float m_rearAeroHeight;
    float m_frontRollAngle;
    float m_rearRollAngle;
    float m_chassisYaw;
    float m_chassisPitch;
    float m_wheelCamber[4];
    float m_wheelCamberGain[4];
};

struct TimeTrialDataSet {
    uint8 m_carIdx;
    uint8 m_teamId;
    uint32 m_lapTimeInMS;
    uint32 m_sector1TimeInMS;
    uint32 m_sector2TimeInMS;
    uint32 m_sector3TimeInMS;
    uint8 m_tractionControl;
    uint8 m_gearboxAssist;
    uint8 m_antiLockBrakes;
    uint8 m_equalCarPerformance;
    uint8 m_customSetup;
    uint8 m_valid;
};

struct PacketTimeTrialData {
    PacketHeader m_header;
    TimeTrialDataSet m_playerSessionBestDataSet;
    TimeTrialDataSet m_personalBestDataSet;
    TimeTrialDataSet m_rivalDataSet;
};

struct PacketLapPositionsData {
    PacketHeader m_header;
    uint8 m_numLaps;
    uint8 m_lapStart;
    uint8 m_positionForVehicleIdx[50][22];
};
"""

CTYPE_MAPPings = {
    "uint8": "ctypes.c_uint8",
    "int8": "ctypes.c_int8",
    "uint16": "ctypes.c_uint16",
    "int16": "ctypes.c_int16",
    "uint32": "ctypes.c_uint32",
    "int32": "ctypes.c_int32",
    "uint64": "ctypes.c_uint64",
    "int64": "ctypes.c_int64",
    "float": "ctypes.c_float",
    "double": "ctypes.c_double",
    "char": "ctypes.c_char",
}

output = [
    "import ctypes",
    "",
    "class PacketMixin:",
    "    def to_dict(self):",
    "        res = {}",
    "        for field, _ in self._fields_:",
    "            val = getattr(self, field)",
    "            if isinstance(val, ctypes.Array):",
    "                if hasattr(val, '_type_') and val._type_ == ctypes.c_char:",
    "                    res[field] = val.value.decode('utf-8', errors='replace')",
    "                else:",
    "                    res[field] = [x.to_dict() if hasattr(x, 'to_dict') else x for x in val]",
    "            elif hasattr(val, 'to_dict'):",
    "                res[field] = val.to_dict()",
    "            else:",
    "                res[field] = val",
    "        return res",
    "",
]

struct_pattern = re.compile(r"struct\s+(\w+)\s*\{([^}]+)\};")
field_pattern = re.compile(r"\s*([\w]+)\s+([\w\[\]]+);")
array_pattern = re.compile(r"(\w+)\[(\d+)\]")
array_2d_pattern = re.compile(r"(\w+)\[(\d+)\]\[(\d+)\]")

for m in struct_pattern.finditer(raw_text):
    struct_name = m.group(1)
    body = m.group(2)
    
    output.append(f"class {struct_name}(ctypes.LittleEndianStructure, PacketMixin):")
    output.append("    _pack_ = 1")
    output.append("    _fields_ = [")
    
    for line in body.splitlines():
        # strip comments
        if "//" in line:
            line = line[:line.index("//")]
        line = line.strip()
        if not line: continue
        
        parts = line.split()
        if len(parts) >= 2:
            ctype_raw = parts[0]
            field_raw = parts[1].replace(";", "")
            
            # handle field arrays
            if "[22]" in field_raw and "positionForVehicleIdx" in field_raw:
                # 2D array
                match = array_2d_pattern.match(field_raw)
                if match:
                    base_field = match.group(1)
                    dim1 = int(match.group(2))
                    dim2 = int(match.group(3))
                    ctype_mapped = CTYPE_MAPPings.get(ctype_raw, ctype_raw)
                    output.append(f"        (\"{base_field}\", {ctype_mapped} * {dim2} * {dim1}),")
            elif "[" in field_raw and not "positionForVehicleIdx" in field_raw:
                match = array_pattern.match(field_raw)
                if match:
                    base_field = match.group(1)
                    size = int(match.group(2))
                    ctype_mapped = CTYPE_MAPPings.get(ctype_raw, ctype_raw)
                    output.append(f"        (\"{base_field}\", {ctype_mapped} * {size}),")
            else:
                ctype_mapped = CTYPE_MAPPings.get(ctype_raw, ctype_raw)
                output.append(f"        (\"{field_raw}\", {ctype_mapped}),")
                
    output.append("    ]")
    output.append("")
    
# Now append EventDataDetails Union and PacketEventData which I do manually because of the union.

event_union = """
class FastestLapData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
        ("lapTime", ctypes.c_float),
    ]

class RetirementData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
        ("reason", ctypes.c_uint8),
    ]

class TeamMateInPitsData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
    ]

class RaceWinnerData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
    ]

class PenaltyData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("penaltyType", ctypes.c_uint8),
        ("infringementType", ctypes.c_uint8),
        ("vehicleIdx", ctypes.c_uint8),
        ("otherVehicleIdx", ctypes.c_uint8),
        ("time", ctypes.c_uint8),
        ("lapNum", ctypes.c_uint8),
        ("placesGained", ctypes.c_uint8),
    ]

class SpeedTrapData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
        ("speed", ctypes.c_float),
        ("isOverallFastestInSession", ctypes.c_uint8),
        ("isDriverFastestInSession", ctypes.c_uint8),
        ("fastestVehicleIdxInSession", ctypes.c_uint8),
        ("fastestSpeedInSession", ctypes.c_float),
    ]

class StartLightsData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("numLights", ctypes.c_uint8),
    ]

class DriveThroughPenaltyServedData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
    ]

class StopGoPenaltyServedData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicleIdx", ctypes.c_uint8),
        ("stopTime", ctypes.c_float),
    ]

class FlashbackData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("flashbackFrameIdentifier", ctypes.c_uint32),
        ("flashbackSessionTime", ctypes.c_float),
    ]

class ButtonsData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("buttonStatus", ctypes.c_uint32),
    ]

class OvertakeData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("overtakingVehicleIdx", ctypes.c_uint8),
        ("beingOvertakenVehicleIdx", ctypes.c_uint8),
    ]

class SafetyCarData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("safetyCarType", ctypes.c_uint8),
        ("eventType", ctypes.c_uint8),
    ]

class CollisionData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("vehicle1Idx", ctypes.c_uint8),
        ("vehicle2Idx", ctypes.c_uint8),
    ]

class EventDataDetails(ctypes.Union, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("FastestLap", FastestLapData),
        ("Retirement", RetirementData),
        ("TeamMateInPits", TeamMateInPitsData),
        ("RaceWinner", RaceWinnerData),
        ("Penalty", PenaltyData),
        ("SpeedTrap", SpeedTrapData),
        ("StartLights", StartLightsData),
        ("DriveThroughPenaltyServed", DriveThroughPenaltyServedData),
        ("StopGoPenaltyServed", StopGoPenaltyServedData),
        ("Flashback", FlashbackData),
        ("Buttons", ButtonsData),
        ("Overtake", OvertakeData),
        ("SafetyCar", SafetyCarData),
        ("Collision", CollisionData),
    ]

class PacketEventData(ctypes.LittleEndianStructure, PacketMixin):
    _pack_ = 1
    _fields_ = [
        ("m_header", PacketHeader),
        ("m_eventStringCode", ctypes.c_char * 4),
        ("m_eventDetails", EventDataDetails),
    ]
    
    def get_event_type(self):
        return self.m_eventStringCode.decode('ascii')
"""

output.append(event_union)

import os
os.makedirs("/Users/aakashsingh/Documents/Developer/f1-game-telemetry/f1_25_telemetry", exist_ok=True)
with open("/Users/aakashsingh/Documents/Developer/f1-game-telemetry/f1_25_telemetry/packets.py", "w") as f:
    f.write("\n".join(output))

print("Created packets.py")
