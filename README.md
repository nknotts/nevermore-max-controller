![Unit Tests](https://github.com/nknotts/nevermore-max-controller/actions/workflows/python.yml/badge.svg)

# Nevermore Max Controller

Nevermore Max Controller source code

## HOWTO

### Firmware

This firmware is written for the [Raspberry Pi Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/).

The firmware is written in [CircuitPython](https://docs.circuitpython.org/en/7.3.x/README.html). [Download version 7.3 for the Pico](https://circuitpython.org/board/raspberry_pi_pico/)

* Connect the Pi Pico USB to your laptop
* Ensure CircuitPython 7.3 is installed on the Pico.
* Copy the full contents of the [firmware](firmware) folder to the root of the Pi Pico (volume name `CIRCUITPY`)
* Anytime `boot.py` is modified, power cycle the Pico for the changes to take effect.


### Test GUI

A Python REPL and data connection are achieved over a single USB connection to the Pi Pico. See [usb_cdc](https://docs.circuitpython.org/en/7.3.x/shared-bindings/usb_cdc/index.html#module-usb_cdc) for more.

```
On Windows, each Serial is visible as a separate COM port. The ports will often be assigned consecutively, console first, but this is not always true.

On Linux, the ports are typically /dev/ttyACM0 and /dev/ttyACM1. The console port will usually be first.

On MacOS, the ports are typically /dev/cu.usbmodem<something>. The something varies based on the USB bus and port used. The console port will usually be first.
```

The `console` port refers to the REPL/interactive port, and the `data` port refers to the data/communcations port.

 * `python3 -m venv env`
 * `source env/bin/activate` (see [venv](https://docs.python.org/3/library/venv.html) for Windows)
 * `pip3 install -r requirements_dev.txt`
 * `python3 test_gui.py`

From the drop down, select the desired serial port. Selecting a serial port will automatically connect.

## Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

* [Cookiecutter](https://github.com/audreyr/cookiecutter)
* [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
