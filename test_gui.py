#!/usr/bin/env python3

import logging
from typing import Union
import time
from collections import deque

import serial
import serial.tools.list_ports

import dearpygui.dearpygui as dpg

from firmware import messagepacket
from firmware import messages


ser: Union[None, serial.Serial] = None

VERSION_TAG = "version_box"
CONNECTION_TEXT_TAG = "connection_text"
CONNECTION_CIRCLE_TAG = "connection_circle"
SERIAL_PORTS_TAG = "serial_ports_combo"
SERIAL_CONNECT_TAG = "serial_port_connect"
SERIAL_DISCONNECT_TAG = "serial_port_disconnect"
SERIAL_REFRESH_TAG = "serial_refresh"
TEXT_BOX_TAG = "text_box"
SAVE_BOX_TAG = "save_box"
STATE_SLIDER_TAG = "state_slider"
TEMPERATURE_TIME_TAG = "temperature_time"
TEMPERATURE_VALUE_TAG = "temperature_value"
IN_DHT_TEMP_SERIES_TAG = "in_dht_temp_series"
OUT_DHT_TEMP_SERIES_TAG = "out_dht_temp_series"
IN_BME_TEMP_SERIES_TAG = "in_bme_temp_series"
OUT_BME_TEMP_SERIES_TAG = "out_bme_temp_series"
HUMIDITY_TIME_TAG = "humidity_time"
HUMIDITY_VALUE_TAG = "humidity_value"
IN_DHT_HUMIDITY_SERIES_TAG = "in_dht_humidity_series"
OUT_DHT_HUMIDITY_SERIES_TAG = "out_dht_humidity_series"
IN_BME_HUMIDITY_SERIES_TAG = "in_bme_humidity_series"
OUT_BME_HUMIDITY_SERIES_TAG = "out_bme_humidity_series"
IN_PRESSURE_SERIES_TAG = "in_pressure_series"
OUT_PRESSURE_SERIES_TAG = "out_pressure_series"
PRESSURE_TIME_TAG = "pressure_time"
PRESSURE_VALUE_TAG = "pressure_value"
IN_CO2_SERIES_TAG = "in_co2_series"
OUT_CO2_SERIES_TAG = "out_co2_series"
CO2_TIME_TAG = "co2_time"
CO2_VALUE_TAG = "co2_value"
IN_TVOC_SERIES_TAG = "in_tvoc_series"
OUT_TVOC_SERIES_TAG = "out_tvoc_series"
TVOC_TIME_TAG = "tvoc_time"
TVOC_VALUE_TAG = "tvco_value"


def save_clicked(sender, app_data):
    dpg.configure_item(SAVE_BOX_TAG, enabled=False)
    # asyncio.run_coroutine_threadsafe(save())


def setup_logging():
    logging.basicConfig(
        format="%(threadName)10s | %(asctime)s.%(msecs)03d | %(levelname)8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)


def item_visibility(tag: str, is_visible: bool):
    if is_visible:
        dpg.show_item(tag)
    else:
        dpg.hide_item(tag)


def update_serial_button_enablement():
    global ser
    is_port_selected = True if dpg.get_value(SERIAL_PORTS_TAG) else False

    connect_visible = True if (is_port_selected and not ser) else False
    disconnect_visible = True if (is_port_selected and ser) else False
    item_visibility(SERIAL_CONNECT_TAG, connect_visible)
    item_visibility(SERIAL_DISCONNECT_TAG, disconnect_visible)

    combo_enabled = True if not ser else False
    dpg.configure_item(STATE_SLIDER_TAG, enabled=(not combo_enabled))

    if ser:
        dpg.set_value(CONNECTION_TEXT_TAG, ser.port)
        dpg.configure_item(CONNECTION_CIRCLE_TAG, color=[0, 255, 0], fill=[0, 255, 0])
    else:
        dpg.set_value(CONNECTION_TEXT_TAG, "")
        dpg.configure_item(CONNECTION_CIRCLE_TAG, color=[255, 0, 0], fill=[255, 0, 0])


def connect():
    global ser
    serial_port = dpg.get_value(SERIAL_PORTS_TAG)
    try:
        ser = serial.Serial(serial_port, baudrate=115200)
        dpg.set_value(VERSION_TAG, "")
        ser.write(messages.VersionRequest().serialize())
        ser.write(
            messages.StateChangeRequest(dpg.get_value(STATE_SLIDER_TAG)).serialize()
        )
    except serial.SerialException as e:
        ser = None
        logging.error(f"Failed to open serial port: {e}")

    update_serial_button_enablement()


def serial_port_selected(sender, app):
    connect()


def refresh_button_clicked(sender, app):
    dpg.configure_item(SERIAL_PORTS_TAG, items=get_serial_ports())
    update_serial_button_enablement()


def connect_button_clicked(sender, app):
    connect()


def state_changed(sender, app):
    global ser
    if ser:
        ser.write(
            messages.StateChangeRequest(dpg.get_value(STATE_SLIDER_TAG)).serialize()
        )


def close_serial():
    global ser
    ser_copy = ser
    ser = None
    if ser_copy:
        ser_copy.close()
    update_serial_button_enablement()


def disconnect_button_clicked(sender, app):
    close_serial()


def get_serial_ports():
    return sorted([port.device for port in serial.tools.list_ports.comports()])


MAX_DATA_LEN = 300

in_dht_temp_data = deque([], maxlen=MAX_DATA_LEN)
out_dht_temp_data = deque([], maxlen=MAX_DATA_LEN)
in_bme_temp_data = deque([], maxlen=MAX_DATA_LEN)
out_bme_temp_data = deque([], maxlen=MAX_DATA_LEN)
in_dht_humidity_data = deque([], maxlen=MAX_DATA_LEN)
out_dht_humidity_data = deque([], maxlen=MAX_DATA_LEN)
in_bme_humidity_data = deque([], maxlen=MAX_DATA_LEN)
out_bme_humidity_data = deque([], maxlen=MAX_DATA_LEN)
in_co2_data = deque([], maxlen=MAX_DATA_LEN)
out_co2_data = deque([], maxlen=MAX_DATA_LEN)
in_tvoc_data = deque([], maxlen=MAX_DATA_LEN)
out_tvoc_data = deque([], maxlen=MAX_DATA_LEN)
in_pressure_data = deque([], maxlen=MAX_DATA_LEN)
out_pressure_data = deque([], maxlen=MAX_DATA_LEN)


def plot_data(data: deque, val):
    data.append([time.time(), val])
    return [list(x[0] for x in data), list(x[1] for x in data)]


def received_msg(msg: messagepacket.MessagePacket):
    try:
        if msg.msg_id == messages.VersionResponse.MsgId:
            resp = messages.VersionResponse.from_message(msg)
            dpg.set_value(VERSION_TAG, resp.version)
        elif msg.msg_id == messages.StateChangeResponse.MsgId:
            resp = messages.StateChangeResponse.from_message(msg)
            logging.info(f"Received: {resp}")
        elif msg.msg_id == messages.SensorReading.MsgId:
            sensor_data = messages.SensorReading.from_message(msg)
            logging.info(f"GOT SENSOR: {sensor_data}")
            global in_dht_temp_data, out_dht_temp_data, in_bme_temp_data, out_bme_temp_data, humidity_data
            dpg.set_value(
                IN_DHT_TEMP_SERIES_TAG,
                plot_data(in_dht_temp_data, sensor_data.in_dht_temp_C),
            )
            dpg.set_value(
                OUT_DHT_TEMP_SERIES_TAG,
                plot_data(out_dht_temp_data, sensor_data.out_dht_temp_C),
            )
            dpg.set_value(
                IN_BME_TEMP_SERIES_TAG,
                plot_data(in_bme_temp_data, sensor_data.in_bme_temp_C),
            )
            dpg.set_value(
                OUT_BME_TEMP_SERIES_TAG,
                plot_data(out_bme_temp_data, sensor_data.out_bme_temp_C),
            )
            dpg.fit_axis_data(TEMPERATURE_TIME_TAG)
            dpg.fit_axis_data(TEMPERATURE_VALUE_TAG)

            dpg.set_value(
                IN_DHT_HUMIDITY_SERIES_TAG,
                plot_data(in_dht_humidity_data, sensor_data.in_dht_humidity_rh),
            )
            dpg.set_value(
                OUT_DHT_HUMIDITY_SERIES_TAG,
                plot_data(out_dht_humidity_data, sensor_data.out_dht_humidity_rh),
            )
            dpg.set_value(
                IN_BME_HUMIDITY_SERIES_TAG,
                plot_data(in_bme_humidity_data, sensor_data.in_bme_humidity_rh),
            )
            dpg.set_value(
                OUT_BME_HUMIDITY_SERIES_TAG,
                plot_data(out_bme_humidity_data, sensor_data.out_bme_humidity_rh),
            )
            dpg.fit_axis_data(HUMIDITY_TIME_TAG)
            dpg.fit_axis_data(HUMIDITY_VALUE_TAG)

            dpg.set_value(
                IN_PRESSURE_SERIES_TAG,
                plot_data(in_pressure_data, sensor_data.in_bme_pressure_hPa),
            )
            dpg.set_value(
                OUT_PRESSURE_SERIES_TAG,
                plot_data(out_pressure_data, sensor_data.out_bme_pressure_hPa),
            )
            dpg.fit_axis_data(PRESSURE_TIME_TAG)
            dpg.fit_axis_data(PRESSURE_VALUE_TAG)

            dpg.set_value(
                IN_CO2_SERIES_TAG,
                plot_data(in_co2_data, sensor_data.in_sgp_eCO2),
            )
            dpg.set_value(
                OUT_CO2_SERIES_TAG,
                plot_data(out_co2_data, sensor_data.out_sgp_eCO2),
            )
            dpg.fit_axis_data(CO2_TIME_TAG)
            dpg.fit_axis_data(CO2_VALUE_TAG)

            dpg.set_value(
                IN_TVOC_SERIES_TAG,
                plot_data(in_tvoc_data, sensor_data.in_sgp_TVOC),
            )
            dpg.set_value(
                OUT_TVOC_SERIES_TAG,
                plot_data(out_tvoc_data, sensor_data.out_sgp_TVOC),
            )
            dpg.fit_axis_data(TVOC_TIME_TAG)
            dpg.fit_axis_data(TVOC_VALUE_TAG)
        else:
            logging.error(f"Unhandled: {msg}")
    except messages.MessageParseError as e:
        logging.error(f"Failed to parse msg - {e}")


def main():
    dpg.create_context()
    dpg.create_viewport(title="Nevermore Max Controller Test GUI")

    parser = messagepacket.MessageParser()

    def serial_read_loop():
        global ser
        try:
            if ser and ser.in_waiting > 0:
                parser.append(ser.read(ser.in_waiting))
        except OSError:
            logging.error(f"Read Error - closing")
            close_serial()
        msg = parser.parse()
        if msg:
            received_msg(msg)

    with dpg.window(label="Example Window", tag="Primary Window"):
        with dpg.group(horizontal=True):
            dpg.add_combo(
                get_serial_ports(), callback=serial_port_selected, tag=SERIAL_PORTS_TAG
            )
            dpg.add_button(
                label="Refresh", callback=refresh_button_clicked, tag=SERIAL_REFRESH_TAG
            )
            dpg.add_button(
                label="Connect", callback=connect_button_clicked, tag=SERIAL_CONNECT_TAG
            )
            dpg.add_button(
                label="Disconnect",
                callback=disconnect_button_clicked,
                tag=SERIAL_DISCONNECT_TAG,
            )

        with dpg.group(horizontal=True):
            dpg.add_text("Connection:")
            circle_size = 16
            with dpg.drawlist(width=circle_size, height=circle_size):
                dpg.draw_circle(
                    center=[circle_size / 2, circle_size / 2],
                    radius=circle_size / 2,
                    color=[255, 0, 0],
                    fill=[255, 0, 0],
                    tag=CONNECTION_CIRCLE_TAG,
                )
            dpg.add_text("", tag=CONNECTION_TEXT_TAG)

        with dpg.group(horizontal=True):
            dpg.add_text("Version: ")
            dpg.add_text("", tag=VERSION_TAG)

        with dpg.group(horizontal=True):
            dpg.add_text("State: ")
            dpg.add_slider_int(
                default_value=42,
                min_value=0,
                max_value=255,
                callback=state_changed,
                tag=STATE_SLIDER_TAG,
            )

        dpg.add_button(label="Toggle", tag=SAVE_BOX_TAG)  # does nothing at the moment

        with dpg.subplots(5, 1, label="Sensor Data", width=-1, height=-1):
            with dpg.plot():
                dpg.add_plot_axis(
                    dpg.mvXAxis, label="Time", time=True, tag=TEMPERATURE_TIME_TAG
                )
                dpg.add_plot_axis(
                    dpg.mvYAxis, label="Temperature (C)", tag=TEMPERATURE_VALUE_TAG
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="DHT22 (In)",
                    parent=TEMPERATURE_VALUE_TAG,
                    tag=IN_DHT_TEMP_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="DHT22 (Out)",
                    parent=TEMPERATURE_VALUE_TAG,
                    tag=OUT_DHT_TEMP_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (In)",
                    parent=TEMPERATURE_VALUE_TAG,
                    tag=IN_BME_TEMP_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (Out)",
                    parent=TEMPERATURE_VALUE_TAG,
                    tag=OUT_BME_TEMP_SERIES_TAG,
                )
                dpg.add_plot_legend()

            with dpg.plot():
                dpg.add_plot_axis(
                    dpg.mvXAxis, label="Time", time=True, tag=HUMIDITY_TIME_TAG
                )
                dpg.add_plot_axis(
                    dpg.mvYAxis, label="Humidity (%)", tag=HUMIDITY_VALUE_TAG
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="DHT22 (In)",
                    parent=HUMIDITY_VALUE_TAG,
                    tag=IN_DHT_HUMIDITY_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="DHT22 (Out)",
                    parent=HUMIDITY_VALUE_TAG,
                    tag=OUT_DHT_HUMIDITY_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (In)",
                    parent=HUMIDITY_VALUE_TAG,
                    tag=IN_BME_HUMIDITY_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (Out)",
                    parent=HUMIDITY_VALUE_TAG,
                    tag=OUT_BME_HUMIDITY_SERIES_TAG,
                )
                dpg.add_plot_legend()

            with dpg.plot():
                dpg.add_plot_axis(
                    dpg.mvXAxis, label="Time", time=True, tag=PRESSURE_TIME_TAG
                )
                dpg.add_plot_axis(
                    dpg.mvYAxis, label="Pressure (hPa)", tag=PRESSURE_VALUE_TAG
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (In)",
                    parent=PRESSURE_VALUE_TAG,
                    tag=IN_PRESSURE_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="BME680 (Out)",
                    parent=PRESSURE_VALUE_TAG,
                    tag=OUT_PRESSURE_SERIES_TAG,
                )
                dpg.add_plot_legend()

            with dpg.plot():
                dpg.add_plot_axis(
                    dpg.mvXAxis, label="Time", time=True, tag=CO2_TIME_TAG
                )
                dpg.add_plot_axis(dpg.mvYAxis, label="CO2 (ppm)", tag=CO2_VALUE_TAG)
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="SGP30 (In)",
                    parent=CO2_VALUE_TAG,
                    tag=IN_CO2_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="SGP30 (Out)",
                    parent=CO2_VALUE_TAG,
                    tag=OUT_CO2_SERIES_TAG,
                )
                dpg.add_plot_legend()

            with dpg.plot():
                dpg.add_plot_axis(
                    dpg.mvXAxis, label="Time", time=True, tag=TVOC_TIME_TAG
                )
                dpg.add_plot_axis(dpg.mvYAxis, label="TVOC (ppb)", tag=TVOC_VALUE_TAG)
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="SGP30 (In)",
                    parent=TVOC_VALUE_TAG,
                    tag=IN_TVOC_SERIES_TAG,
                )
                dpg.add_line_series(
                    x=[],
                    y=[],
                    label="SGP30 (Out)",
                    parent=TVOC_VALUE_TAG,
                    tag=OUT_TVOC_SERIES_TAG,
                )
                dpg.add_plot_legend()

    update_serial_button_enablement()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        # serial_read_loop() should be in its own thread
        # however, this is just a test application so performance is not critical
        serial_read_loop()
    dpg.destroy_context()


if __name__ == "__main__":
    setup_logging()
    main()
