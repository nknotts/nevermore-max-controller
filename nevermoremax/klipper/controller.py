import logging

from .serial import SerialPort
from ..firmware import messagepacket


class NevermoreMaxController:
    def __init__(self, config):
        serial_port = config.get("serial-port")
        serial_baud = config.get("serial-baud", default=115200)
        self.serial = SerialPort(serial_port, serial_baud)
        self.serial_parser = messagepacket.MessageParser()

        self.printer = config.get_printer()
        self.printer.get_reactor().register_fd(self.serial.fd, self._serial_data_ready)

    def _serial_data_ready(self, eventtime):
        data = self.serial.read()
        self.serial_parser.append(data)
        msg, _ = self.serial_parser.parse()
        if msg:
            self._received_message(msg)

    def _received_message(self, msg):
        logging.info("Received NMC Msg", msg)
