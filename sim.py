#!/usr/bin/env python3

import logging
import time
import argparse

import serial

from nevermoremax.firmware import messagepacket
from nevermoremax.firmware import messages
from nevermoremax.firmware import sensorssim


def received_msg(msg: messagepacket.MessagePacket, ser: serial.Serial):
    try:
        if msg.msg_id == messages.VersionRequest.MsgId:
            _req = messages.VersionRequest.from_message(msg)
            logging.info(f"Received: {_req}")
            ser.write(messages.VersionResponse("0.0.1-sim").serialize())
        elif msg.msg_id == messages.StateChangeRequest.MsgId:
            _req = messages.StateChangeRequest.from_message(msg)
            logging.info(f"Received: {_req}")
            ser.write(messages.StateChangeResponse(_req.state).serialize())
        else:
            logging.info(f"ERROR: unhandled message - {msg}")
    except messages.MessageParseError as e:
        logging.error(f"Failed to parse msg - {e}")


def main(port):
    ser = serial.Serial(port, 115200, timeout=0.1)
    sensors = sensorssim.SimSensors()
    parser = messagepacket.MessageParser()

    t_last = time.monotonic()
    while True:
        parser.append(ser.read(1))
        now = time.monotonic()
        if (now - t_last) > 1:
            t_last = now
            msg = messages.SensorReading(*sensors.sample().data())
            ser.write(msg.serialize())
        msg, _ = parser.parse()
        if msg:
            received_msg(msg, ser)


def setup_logging():
    logging.basicConfig(
        format="%(threadName)10s | %(asctime)s.%(msecs)03d | %(levelname)8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("serial_port")
    args = parser.parse_args()

    main(args.serial_port)
