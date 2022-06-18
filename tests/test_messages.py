#!/usr/bin/env python

"""Tests for `nevermore_max_controller` package."""


import pytest


from ..firmware import messages
from ..firmware import messagepacket


def parse_msg(msg: bytes):
    parser = messagepacket.MessageParser()
    parser.append(msg)
    msg, _ = parser.parse()
    assert msg
    return msg


def test_version_request():
    request_in = messages.VersionRequest()
    request_msg = parse_msg(request_in.serialize())
    request_out = messages.VersionRequest.from_message(request_msg)
    assert request_out


def test_version_response():
    VERSION_STR = "test-version"
    response_in = messages.VersionResponse(VERSION_STR)
    response_msg = parse_msg(response_in.serialize())
    response_out = messages.VersionResponse.from_message(response_msg)
    assert response_out.version == VERSION_STR


def test_state_change_request():
    STATE = 0x42
    request_in = messages.StateChangeRequest(STATE)
    request_msg = parse_msg(request_in.serialize())
    request_out = messages.StateChangeRequest.from_message(request_msg)
    assert request_out.state == STATE


def test_state_change_response():
    STATE = 42
    response_in = messages.StateChangeResponse(STATE)
    response_msg = parse_msg(response_in.serialize())
    response_out = messages.StateChangeResponse.from_message(response_msg)
    assert response_out.state == STATE


def test_sensor_reading():
    reading_in = messages.SensorReading(
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
    )
    reading_msg = parse_msg(reading_in.serialize())
    reading_out = messages.SensorReading.from_message(reading_msg)
    assert reading_in.in_dht_temp_C == reading_out.in_dht_temp_C
    assert reading_in.in_dht_humidity_rh == reading_out.in_dht_humidity_rh
    assert reading_in.in_sgp_eCO2 == reading_out.in_sgp_eCO2
    assert reading_in.in_sgp_TVOC == reading_out.in_sgp_TVOC
    assert reading_in.in_bme_temp_C == reading_out.in_bme_temp_C
    assert reading_in.in_bme_gas == reading_out.in_bme_gas
    assert reading_in.in_bme_humidity_rh == reading_out.in_bme_humidity_rh
    assert reading_in.in_bme_pressure_hPa == reading_out.in_bme_pressure_hPa
    assert reading_in.in_bme_altitude_m == reading_out.in_bme_altitude_m
    assert reading_in.out_dht_temp_C == reading_out.out_dht_temp_C
    assert reading_in.out_dht_humidity_rh == reading_out.out_dht_humidity_rh
    assert reading_in.out_sgp_eCO2 == reading_out.out_sgp_eCO2
    assert reading_in.out_sgp_TVOC == reading_out.out_sgp_TVOC
    assert reading_in.out_bme_temp_C == reading_out.out_bme_temp_C
    assert reading_in.out_bme_gas == reading_out.out_bme_gas
    assert reading_in.out_bme_humidity_rh == reading_out.out_bme_humidity_rh
    assert reading_in.out_bme_pressure_hPa == reading_out.out_bme_pressure_hPa
    assert reading_in.out_bme_altitude_m == reading_out.out_bme_altitude_m
