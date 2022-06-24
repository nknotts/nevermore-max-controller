import logging
import serial

from .firmware import messagepacket
from .firmware import messages

class NevermoreTemperature:
    def __init__(self, config, setup_source_callback_name):
        self.name = config.get_name().split()[-1]
        self.printer = config.get_printer()
        controller = self.printer.load_object(config, 'nevermoremax')
        setup_source_callback = getattr(controller, setup_source_callback_name)
        setup_source_callback(self._recv_measurement)
        self.temperature_callback = lambda time, val: None
        self.min_temp = self.max_temp = 0
        self.printer.add_object("bme280 " + self.name, self) # display measurement data in mainail
        self.measurement = {}

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, temperature_callback):
        self.temperature_callback = temperature_callback

    def _recv_measurement(self, eventtime, measurement):
        self.measurement = measurement

        temp = measurement['temperature']
        self.temperature_callback(eventtime, temp)

        if temp < self.min_temp:
            self.printer.invoke_shutdown(
                "%s temperature %0.1f below minimum temperature of %0.1f."
                % (self.name, temp, self.min_temp,))
        if temp > self.max_temp:
            self.printer.invoke_shutdown(
                "%s temperature %0.1f above maximum temperature of %0.1f."
                % (self.name, temp, self.max_temp,))

    def get_status(self, eventtime):
        return self.measurement


def create_intake(config):
    return NevermoreTemperature(config, 'setup_intake_temperature_callback')

def create_exhaust(config):
    return NevermoreTemperature(config, 'setup_exhaust_temperature_callback')

class NevermoreMaxController:
    def __init__(self, config):
        logging.info("NevermoreMaxController __init__")
        serial_port = config.get("serial")
        serial_baud = config.get("baud", default=115200)
        self.serial = serial.Serial(serial_port, serial_baud, timeout=0, write_timeout=0)
        self.serial_parser = messagepacket.MessageParser()
        self.printer = config.get_printer()
        self.printer.get_reactor().register_fd(self.serial.fileno(), self._serial_data_ready)
        self.intake_temperature_cb = lambda time, val: None
        self.exhaust_temperature_cb = lambda time, val: None
        self.gcode = self.printer.lookup_object('gcode')

        self.gcode.register_command(
            'GET_NEVERMORE_MAX_FIRMWARE_VERSION',
            self._request_version,
            desc="Request Nevermore Max Controller Firmware Version")

        self.gcode.register_command(
            'GET_NEVERMORE_MAX_MEASUREMENT',
            self._get_measurement,
            desc="Print Detailed Nevermore Max Controller Sensor Measurement")


        self.gcode.register_command(
            'SET_NEVERMORE_MAX_STATE',
            self._set_state,
            desc="Set Nevermore Max Controller State")

        self.measurement = {}

    def setup_intake_temperature_callback(self, callback):
        self.intake_temperature_cb = callback

    def setup_exhaust_temperature_callback(self, callback):
        self.exhaust_temperature_cb = callback

    def get_status(self, eventtime):
        return self.measurement

    def _serial_data_ready(self, eventtime):
        data = self.serial.read(self.serial.in_waiting)

        self.serial_parser.append(data)
        msg, _ = self.serial_parser.parse()
        if msg:
            self._received_message(msg, eventtime)

    def _request_version(self, gcmd):
        self.serial.write(messages.VersionRequest().serialize())
        logging.info("Requesting Nevermore Max Firmware Version")

    def _set_state(self, gcmd):
        state = gcmd.get_int('STATE', default=None, minval=0, maxval=255)
        if state is not None:
            self.serial.write(messages.StateChangeRequest(state).serialize())
        else:
            gcmd.respond_info("STATE is required")

    def _get_measurement(self, gcmd):
        self.gcode.respond_info("Nevermore Max Measurement: {}".format(self.measurement))

    def _received_message(self, msg, eventtime):
        #logging.info("Received NMC Msg: {}".format(msg))
        if msg.msg_id == messages.SensorReading.MsgId:
            reading = messages.SensorReading.from_message(msg)
            #logging.info("Received: {}".format(reading))
            self.intake_temperature_cb(eventtime, {
                'temperature': reading.in_bme_temp_C,
                'humidity': reading.in_bme_humidity_rh,
                'pressure': reading.in_bme_pressure_hPa,
                'gas': reading.in_bme_gas
            })
            self.exhaust_temperature_cb(eventtime, {
                'temperature': reading.out_bme_temp_C,
                'humidity': reading.out_bme_humidity_rh,
                'pressure': reading.out_bme_pressure_hPa,
                'gas': reading.out_bme_gas
            })
            self.measurement = {
                'intake': {
                    'temp_C': reading.in_bme_temp_C
                },
                'exhaust': {
                    'temp_C': reading.out_bme_temp_C
                }
            }
        elif msg.msg_id == messages.VersionResponse.MsgId:
            version = messages.VersionResponse.from_message(msg)
            logging.info("Nevermore Max Firmware Version: {}".format(version.version))
            self.gcode.respond_info("Nevermore Max Firmware Version: {}".format(version.version))
        elif msg.msg_id == messages.StateChangeResponse.MsgId:
            state = messages.StateChangeResponse.from_message(msg)
            logging.info("Nevermore Max State: {}".format(state.state))
            self.gcode.respond_info("Nevermore Max State: {}".format(state.state))


def load_config(config):
    pheater = config.get_printer().lookup_object("heaters")
    pheater.add_sensor_factory("nevermore_intake", create_intake)
    pheater.add_sensor_factory("nevermore_exhaust", create_exhaust)

    return NevermoreMaxController(config)
