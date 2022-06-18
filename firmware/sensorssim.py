import time
import random
import math

try:
    from sensordata import SensorData, SensorGroupData
except ImportError:
    from .sensordata import SensorData, SensorGroupData

t0 = time.monotonic()


def sim_value(
    min: float, max: float, period_s: float, phase_s: float, random_range: float
):
    global t0
    t_s = (time.monotonic() - t0) + phase_s
    freq_hz = 1.0 / period_s
    mid = (min + max) / 2.0
    amp = (max - min) / 2.0
    rand = random.uniform(-random_range, random_range)
    return mid + amp * math.sin(2 * math.pi * freq_hz * t_s) + rand


def simulate_group_data(base_t_offset_s: float):
    return SensorGroupData(
        dht_temp_C=sim_value(20, 25, 60, base_t_offset_s, 0.25),
        dht_humidity=sim_value(40, 50, 120, base_t_offset_s, 0.75),
        sgp30_eC02=sim_value(100, 200, 30, base_t_offset_s, 2),
        sgp30_TCOV=sim_value(10, 15, 60, base_t_offset_s, 0.5),
        gme_temp_C=sim_value(20, 25, 60, base_t_offset_s - 2, 0.25),
        gme_gas=sim_value(75, 100, 200, base_t_offset_s, 1),
        gme_humidity=sim_value(40, 50, 120, base_t_offset_s - 2, 0.75),
        gme_pres_hPa=sim_value(990, 1100, 90, base_t_offset_s, 5),
        gme_alt_m=sim_value(500, 550, 60, base_t_offset_s, 2),
    )


class SimSensors:
    def sample(self):
        return SensorData(simulate_group_data(0), simulate_group_data(2))
