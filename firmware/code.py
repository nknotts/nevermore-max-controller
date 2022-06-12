import time
import random
import math

import board
import digitalio
import asyncio
import usb_cdc

from messagepacket import MessageParser, MessagePacket
import messages

VERSION_STRING = "0.0.1"

t0 = time.monotonic()
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


def print_ttag(val: str):
    print(f"{time.monotonic() - t0:8.3f}: {val}")


def toggle_led():
    led.value = not led.value


def schedule_task(fn, duration_s: float, *args):
    async def task(fn, duration_s: float, *args):
        next = time.monotonic()
        while True:
            fn(*args[0])
            next += duration_s
            now = time.monotonic()
            sleep_for = next - now
            # TODO: better handle missed loop timing
            await asyncio.sleep(sleep_for)

    return asyncio.create_task(task(fn, duration_s, args))


def received_msg(msg: MessagePacket):
    uart = usb_cdc.data

    try:
        if msg.msg_id == messages.VersionRequest.MsgId:
            _req = messages.VersionRequest.from_message(msg)
            print_ttag(f"Received: {_req}")
            uart.write(messages.VersionResponse(VERSION_STRING).serialize())
        elif msg.msg_id == messages.StateChangeRequest.MsgId:
            _req = messages.StateChangeRequest.from_message(msg)
            print_ttag(f"Received: {_req}")
            uart.write(messages.StateChangeResponse(_req.state).serialize())
        else:
            print_ttag(f"ERROR: unhandled message - {msg}")
    except messages.MessageParseError as e:
        print_ttag(f"Failed to parse msg - {e}")


async def usb_read_loop():
    uart = usb_cdc.data
    parser = MessageParser()
    while True:
        if uart.in_waiting > 0:
            parser.append(uart.read(uart.in_waiting))
        msg = parser.parse()
        if msg:
            received_msg(msg)
        await asyncio.sleep(0)


def sim_value(
    min: float, max: float, period_s: float, phase_s: float, random_range: float
):
    t_s = (time.monotonic() - t0) + phase_s
    freq_hz = 1.0 / period_s
    mid = (min + max) / 2.0
    amp = (max - min) / 2.0
    rand = random.uniform(-random_range, random_range)
    return mid + amp * math.sin(2 * math.pi * freq_hz * t_s) + rand


def collect_sensor_data():
    uart = usb_cdc.data

    sensor_data = messages.SensorReading(
        in_dht_temp_C=sim_value(20, 25, 60, 0, 0.25),
        in_dht_humidity_rh=sim_value(40, 50, 120, 0, 0.75),
        in_sgp_eCO2=sim_value(100, 200, 30, 0, 2),
        in_sgp_TVOC=sim_value(10, 15, 60, 0, 0.5),
        in_bme_temp_C=sim_value(20, 25, 60, -2, 0.25),
        in_bme_gas=sim_value(75, 100, 200, 0, 1),
        in_bme_humidity_rh=sim_value(40, 50, 120, -2, 0.75),
        in_bme_pressure_hPa=sim_value(990, 1100, 90, 0, 5),
        in_bme_altitude_m=sim_value(500, 550, 60, 0, 2),
        out_dht_temp_C=sim_value(20, 25, 60, 2, 0.25),
        out_dht_humidity_rh=sim_value(40, 50, 120, 2, 0.75),
        out_sgp_eCO2=sim_value(100, 200, 30, 2, 2),
        out_sgp_TVOC=sim_value(10, 15, 60, 2, 0.5),
        out_bme_temp_C=sim_value(20, 25, 60, 4, 0.25),
        out_bme_gas=sim_value(75, 100, 200, 2, 1),
        out_bme_humidity_rh=sim_value(40, 50, 120, 4, 0.75),
        out_bme_pressure_hPa=sim_value(990, 1100, 90, 2, 5),
        out_bme_altitude_m=sim_value(500, 550, 60, 2, 2),
    )
    uart.write(sensor_data.serialize())
    print_ttag(f"Sending: {sensor_data}")


async def main():
    await asyncio.gather(
        schedule_task(collect_sensor_data, 1.0),
        schedule_task(toggle_led, 0.5),
        usb_read_loop(),
    )


asyncio.run(main())
