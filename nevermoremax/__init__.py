from .klipper import controller

def load_config(config):
    pheater = config.get_printer().lookup_object("heaters")
    pheater.add_sensor_factory("nevermore_intake_temperature", controller.IntakeTemperature)
    pheater.add_sensor_factory("nevermore_exhaust_temperature", controller.ExhaustTemperature)

    return controller.NevermoreMaxController(config)
