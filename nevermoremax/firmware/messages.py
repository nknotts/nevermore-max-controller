# -*- coding: future_fstrings -*-

import struct

try:
    from messagepacket import MessagePacket
except ImportError:
    from .messagepacket import MessagePacket


class MessageParseError(Exception):
    pass


class MessageIdError(MessageParseError):
    pass


class PayloadLengthError(MessageParseError):
    pass


class VersionRequest:
    MsgId = 0x00
    PayloadLength = 0

    def __repr__(self):
        return "VersionRequest()"

    @staticmethod
    def from_message(msg):
        if msg.msg_id != VersionRequest.MsgId:
            raise MessageIdError()
        if len(msg.payload) != VersionRequest.PayloadLength:
            raise PayloadLengthError()
        return VersionRequest()

    def serialize(self):
        return MessagePacket(self.MsgId, b"").serialize()


class VersionResponse:
    MsgId = 0x80
    MaxPayloadLength = 60

    def __init__(self, version):
        if len(version) > self.MaxPayloadLength:
            raise MessageParseError()
        self.version = version

    def __repr__(self):
        return f"VersionResponse(version={self.version})"

    @staticmethod
    def from_message(msg):
        if msg.msg_id != VersionResponse.MsgId:
            raise MessageIdError()
        if len(msg.payload) > VersionResponse.MaxPayloadLength:
            raise PayloadLengthError()
        return VersionResponse(msg.payload.decode())

    def serialize(self):
        return MessagePacket(self.MsgId, str.encode(self.version)).serialize()


class StateChangeRequest:
    MsgId = 0x01
    PayloadLength = 1

    def __init__(self, state):
        self.state = state

    def __repr__(self):
        return f"StateChangeRequest(state=0x{self.state:02X})"

    @staticmethod
    def from_message(msg):
        if msg.msg_id != StateChangeRequest.MsgId:
            raise MessageIdError()
        if len(msg.payload) != StateChangeRequest.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack("B", msg.payload)
        return StateChangeRequest(data[0])

    def serialize(self):
        return MessagePacket(self.MsgId, struct.pack("<B", self.state)).serialize()


class StateChangeResponse:
    MsgId = 0x81
    PayloadLength = 1

    def __init__(self, state):
        self.state = state

    def __repr__(self):
        return f"StateChangeResponse(state=0x{self.state:02X})"

    @staticmethod
    def from_message(msg):
        if msg.msg_id != StateChangeResponse.MsgId:
            raise MessageIdError()
        if len(msg.payload) != StateChangeResponse.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack("B", msg.payload)
        return StateChangeResponse(data[0])

    def serialize(self):
        return MessagePacket(self.MsgId, struct.pack("<B", self.state)).serialize()


class SensorReading:
    MsgId = 0x82

    StructFormat = "<HHHHfffffHHHHfffff"  # should match payload length
    PayloadLength = struct.calcsize(StructFormat)

    def __init__(
        self,
        in_dht_temp_C,
        in_dht_humidity_rh,
        in_sgp_eCO2,
        in_sgp_TVOC,
        in_bme_temp_C,
        in_bme_gas,
        in_bme_humidity_rh,
        in_bme_pressure_hPa,
        in_bme_altitude_m,
        out_dht_temp_C,
        out_dht_humidity_rh,
        out_sgp_eCO2,
        out_sgp_TVOC,
        out_bme_temp_C,
        out_bme_gas,
        out_bme_humidity_rh,
        out_bme_pressure_hPa,
        out_bme_altitude_m,
    ):
        self.in_dht_temp_C = in_dht_temp_C
        self.in_dht_humidity_rh = in_dht_humidity_rh
        self.in_sgp_eCO2 = in_sgp_eCO2
        self.in_sgp_TVOC = in_sgp_TVOC
        self.in_bme_temp_C = in_bme_temp_C
        self.in_bme_gas = in_bme_gas
        self.in_bme_humidity_rh = in_bme_humidity_rh
        self.in_bme_pressure_hPa = in_bme_pressure_hPa
        self.in_bme_altitude_m = in_bme_altitude_m
        self.out_dht_temp_C = out_dht_temp_C
        self.out_dht_humidity_rh = out_dht_humidity_rh
        self.out_sgp_eCO2 = out_sgp_eCO2
        self.out_sgp_TVOC = out_sgp_TVOC
        self.out_bme_temp_C = out_bme_temp_C
        self.out_bme_gas = out_bme_gas
        self.out_bme_humidity_rh = out_bme_humidity_rh
        self.out_bme_pressure_hPa = out_bme_pressure_hPa
        self.out_bme_altitude_m = out_bme_altitude_m

    def __repr__(self):
        return f"SensorReading(in{{tempC={self.in_bme_temp_C:.1f}, RH={self.in_bme_humidity_rh:.1f}, hPa={self.in_bme_pressure_hPa:.1f}, eCO2={self.in_sgp_eCO2:.1f}, TVOC={self.in_sgp_TVOC:.1f}}}, out{{tempC={self.out_bme_temp_C:.1f}, RH={self.out_bme_humidity_rh:.1f}, hPa={self.out_bme_pressure_hPa:.1f}, eCO2={self.out_sgp_eCO2:.1f}, TVOC={self.out_sgp_TVOC:.1f}}}"

    @staticmethod
    def from_message(msg):
        if msg.msg_id != SensorReading.MsgId:
            raise MessageIdError()
        if len(msg.payload) != SensorReading.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack(SensorReading.StructFormat, msg.payload)
        return SensorReading(*data)

    def serialize(self):
        return MessagePacket(
            self.MsgId,
            struct.pack(
                self.StructFormat,
                int(self.in_dht_temp_C),
                int(self.in_dht_humidity_rh),
                int(self.in_sgp_eCO2),
                int(self.in_sgp_TVOC),
                self.in_bme_temp_C,
                self.in_bme_gas,
                self.in_bme_humidity_rh,
                self.in_bme_pressure_hPa,
                self.in_bme_altitude_m,
                int(self.out_dht_temp_C),
                int(self.out_dht_humidity_rh),
                int(self.out_sgp_eCO2),
                int(self.out_sgp_TVOC),
                self.out_bme_temp_C,
                self.out_bme_gas,
                self.out_bme_humidity_rh,
                self.out_bme_pressure_hPa,
                self.out_bme_altitude_m,
            ),
        ).serialize()
