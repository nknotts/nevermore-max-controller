import logging

from .serial import SerialPort
from ..firmware import messagepacket
from ..firmware import messages

class IntakeTemperature:
    def __init__(self, config):
        self.printer = config.get_printer()
        controller = self.printer.load_object(config, 'nevermoremax')
        controller.setup_intake_temperature_callback(self.recv_tempeturate)
        logging.info(controller)
        self.temperature_callback = lambda time, val: None
        self.temp = self.min_temp = self.max_temp = 0

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, temperature_callback):
        self.temperature_callback = temperature_callback

    def recv_tempeturate(self, eventtime, temp_C):
        self.temperature_callback(eventtime, temp_C)
        self.temp = temp_C
        if self.temp < self.min_temp:
            self.printer.invoke_shutdown(
                "Nevermore intake temperature %0.1f below minimum temperature of %0.1f."
                % (self.temp, self.min_temp,))
        if self.temp > self.max_temp:
            self.printer.invoke_shutdown(
                "Nevermore intake  temperature %0.1f above maximum temperature of %0.1f."
                % (self.temp, self.max_temp,))

class ExhaustTemperature:
    def __init__(self, config):
        self.printer = config.get_printer()
        controller = self.printer.load_object(config, 'nevermoremax')
        controller.setup_exhaust_temperature_callback(self.recv_tempeturate)
        logging.info(controller)
        self.temperature_callback = lambda time, val: None
        self.temp = self.min_temp = self.max_temp = 0

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, temperature_callback):
        self.temperature_callback = temperature_callback

    def recv_tempeturate(self, eventtime, temp_C):
        self.temperature_callback(eventtime, temp_C)
        self.temp = temp_C
        if self.temp < self.min_temp:
            self.printer.invoke_shutdown(
                "Nevermore exhaust temperature %0.1f below minimum temperature of %0.1f."
                % (self.temp, self.min_temp,))
        if self.temp > self.max_temp:
            self.printer.invoke_shutdown(
                "Nevermore exhaust  temperature %0.1f above maximum temperature of %0.1f."
                % (self.temp, self.max_temp,))

class NevermoreMaxController:
    def __init__(self, config):
        logging.info("NevermoreMaxController __init__")
        serial_port = config.get("serial")
        serial_baud = config.get("baud", default=115200)
        self.serial = SerialPort(serial_port, serial_baud)
        self.serial_parser = messagepacket.MessageParser()
        self.printer = config.get_printer()
        self.printer.get_reactor().register_fd(self.serial.fd, self._serial_data_ready)
        self.intake_temperature_cb = lambda time, val: None
        self.exhaust_temperature_cb = lambda time, val: None

    def setup_intake_temperature_callback(self, callback):
        self.intake_temperature_cb = callback

    def setup_exhaust_temperature_callback(self, callback):
        self.exhaust_temperature_cb = callback

    def _serial_data_ready(self, eventtime):
        data = self.serial.read()

        self.serial_parser.append(data)
        msg, _ = self.serial_parser.parse()
        if msg:
            self._received_message(msg, eventtime)

    def _received_message(self, msg, eventtime):
        #logging.info("Received NMC Msg: {}".format(msg))
        if msg.msg_id == messages.SensorReading.MsgId:
            reading = messages.SensorReading.from_message(msg)
            logging.info("Received: {}".format(reading))
            self.intake_temperature_cb(eventtime, reading.in_bme_temp_C)
            self.exhaust_temperature_cb(eventtime, reading.out_bme_temp_C)

