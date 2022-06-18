from collections import namedtuple

SensorGroupData = namedtuple(
    "SensorGroupData",
    [
        "dht_temp_C",
        "dht_humidity",
        "sgp30_eC02",
        "sgp30_TCOV",
        "gme_temp_C",
        "gme_gas",
        "gme_humidity",
        "gme_pres_hPa",
        "gme_alt_m",
    ],
)


class SensorData:
    def __init__(self, data_in: SensorGroupData, data_out: SensorGroupData):
        self.data_in = data_in
        self.data_out = data_out

    def data(self):
        return self.data_in + self.data_out
