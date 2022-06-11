from .messagepacket import MessagePacket
import struct


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
    def from_message(msg: MessagePacket):
        if msg.msg_id != VersionRequest.MsgId:
            raise MessageIdError()
        if len(msg.payload) != VersionRequest.PayloadLength:
            raise PayloadLengthError()
        return VersionRequest()

    def serialize(self) -> bytes:
        return MessagePacket(self.MsgId, b"").serialize()


class VersionResponse:
    MsgId = 0x80
    MaxPayloadLength = 60

    def __init__(self, version: str):
        if len(version) > self.MaxPayloadLength:
            raise MessageParseError()
        self.version = version

    def __repr__(self):
        return f"VersionResponse(version={self.version})"

    @staticmethod
    def from_message(msg: MessagePacket):
        if msg.msg_id != VersionResponse.MsgId:
            raise MessageIdError()
        if len(msg.payload) > VersionResponse.MaxPayloadLength:
            raise PayloadLengthError()
        return VersionResponse(msg.payload.decode())

    def serialize(self) -> bytes:
        return MessagePacket(self.MsgId, str.encode(self.version)).serialize()


class StateChangeRequest:
    MsgId = 0x01
    PayloadLength = 1

    def __init__(self, state: int):
        self.state = state

    def __repr__(self):
        return f"StateChangeRequest(state=0x{self.state:02X})"

    @staticmethod
    def from_message(msg: MessagePacket):
        if msg.msg_id != StateChangeRequest.MsgId:
            raise MessageIdError()
        if len(msg.payload) != StateChangeRequest.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack("B", msg.payload)
        return StateChangeRequest(data[0])

    def serialize(self) -> bytes:
        return MessagePacket(self.MsgId, struct.pack("<B", self.state)).serialize()


class StateChangeResponse:
    MsgId = 0x81
    PayloadLength = 1

    def __init__(self, state: int):
        self.state = state

    def __repr__(self):
        return f"StateChangeResponse(state=0x{self.state:02X})"

    @staticmethod
    def from_message(msg: MessagePacket):
        if msg.msg_id != StateChangeResponse.MsgId:
            raise MessageIdError()
        if len(msg.payload) != StateChangeResponse.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack("B", msg.payload)
        return StateChangeResponse(data[0])

    def serialize(self) -> bytes:
        return MessagePacket(self.MsgId, struct.pack("<B", self.state)).serialize()


class SensorReading:
    MsgId = 0x82
    PayloadLength = 12
    StructFormat = "<fff"  # should match payload length

    def __init__(self, temp_C: float, humidity: float, pressure_kPa: float):
        self.temp_C = temp_C
        self.humidity = humidity
        self.pressure_kPa = pressure_kPa

    def __repr__(self):
        return f"SensorReading(temp_C={self.temp_C:.1f}, humidity={self.humidity:.1f}, pressure_kPa={self.pressure_kPa:.1f})"

    @staticmethod
    def from_message(msg: MessagePacket):
        if msg.msg_id != SensorReading.MsgId:
            raise MessageIdError()
        if len(msg.payload) != SensorReading.PayloadLength:
            raise PayloadLengthError()
        data = struct.unpack(SensorReading.StructFormat, msg.payload)
        return SensorReading(*data)

    def serialize(self) -> bytes:
        return MessagePacket(
            self.MsgId,
            struct.pack(
                self.StructFormat, self.temp_C, self.humidity, self.pressure_kPa
            ),
        ).serialize()
