from sensordata import SensorData, SensorGroupData

import board
import busio

import adafruit_bme680
import adafruit_sgp30
import adafruit_dht


class Sensors:
    def __init__(self):
        self.i2c0 = busio.I2C(board.GP17, board.GP16)
        self.sgp30_in = adafruit_sgp30.Adafruit_SGP30(self.i2c0)
        self.dht22_in = adafruit_dht.DHT22(board.GP20)
        self.bme680_in = adafruit_bme680.Adafruit_BME680_I2C(self.i2c0, debug=False)

        self.i2c1 = busio.I2C(board.GP19, board.GP18)
        self.sgp30_out = adafruit_sgp30.Adafruit_SGP30(self.i2c1)
        self.dht22_out = adafruit_dht.DHT22(board.GP21)
        self.bme680_out = adafruit_bme680.Adafruit_BME680_I2C(self.i2c1, debug=False)

        self.sgp30_in.iaq_init()
        self.sgp30_in.set_iaq_baseline(0x8973, 0x8AAE)
        # set from real measurements?
        self.sgp30_in.set_iaq_relative_humidity(celcius=22.1, relative_humidity=44)

        self.sgp30_out.iaq_init()
        self.sgp30_out.set_iaq_baseline(0x8973, 0x8AAE)
        # set from real measurements?
        self.sgp30_out.set_iaq_relative_humidity(celcius=22.1, relative_humidity=44)

        # BME68x Temperature Offset
        # You will usually have to add an offset to account for the temperature of
        # the sensor. This is usually around 5 degrees but varies by use. Use a
        # separate temperature sensor to calibrate this one.
        self.bme_temperature_offset_C_in = 5
        self.bme_temperature_offset_C_out = 5

    def sample(self):
        data_in = sample_group(
            self.dht22_in,
            self.sgp30_in,
            self.bme680_in,
            self.bme_temperature_offset_C_in,
        )

        data_out = sample_group(
            self.dht22_out,
            self.sgp30_out,
            self.bme680_out,
            self.bme_temperature_offset_C_out,
        )

        return SensorData(data_in, data_out)


def sample_group(
    dht22: adafruit_dht.DHT22,
    sgp30: adafruit_sgp30.Adafruit_SGP30,
    bme680: adafruit_bme680.Adafruit_BME680_I2C,
    bme_temp_offset_C: float,
) -> SensorGroupData:

    # Measure DHT22a
    dht_temp_C = -1
    dht_humidity = -1
    try:
        dht_temp_C = dht22.temperature
        dht_humidity = dht22.humidity
    except RuntimeError:
        pass
    except Exception as err:
        print(f"DHT22 Error: {err}")

    sgp30_eC02 = sgp30.eCO2
    sgp30_TCOV = sgp30.TVOC

    gme_temp_C = bme680.temperature + bme_temp_offset_C
    gme_gas = bme680.gas
    gme_humidity = bme680.relative_humidity
    gme_pres_hPa = bme680.pressure
    gme_alt_m = bme680.altitude

    return SensorGroupData(
        dht_temp_C,
        dht_humidity,
        sgp30_eC02,
        sgp30_TCOV,
        gme_temp_C,
        gme_gas,
        gme_humidity,
        gme_pres_hPa,
        gme_alt_m,
    )
