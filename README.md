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

### Klipper Plugin

#### Manual Installation

To install this plugin, you need to this entire project directory file into the `extras`
folder of klipper. Like:

```bash
/home/pi/klipper/klippy/extras/nevermore-max-controller
```

An alternative would be to clone this repo and run the `install_klipper.sh` script. Like:

```bash
cd /home/pi
git clone https://github.com/nknotts/nevermore-max-controller.git
./nevermore-max-controller/install_klipper.sh
```

It's safe to execute the install script multiple times.

More on this in the [Moonraker Update Manager](#moonraker-update-manager) section.

#### Moonraker Update Manager

It's possible to keep this extension up to date with the Moonraker's [update manager](https://github.com/Arksine/moonraker/blob/master/docs/configuration.md#update_manager) by
adding this configuration block to the "moonraker.conf" of your printer:

```text
[update_manager client nevermore_max_controller]
type: git_repo
path: ~/nevermore_max_controller
origin: https://github.com/nknotts/nevermore-max-controller.git
install_script: install_klipper.sh
managed_services: klipper
```

This requires this repository to be cloned into your home directory (e.g. /home/pi):

```bash
git clone https://github.com/nknotts/nevermore-max-controller.git
```

The install script assumes that Klipper is also installed in your home directory under
"klipper": `${HOME}/klipper`.

>:point_up: **NOTE:** If your Moonraker is not on a recent version, you may get an error
> with the "managed_services" line!


## Credits

* [VORON](https://vorondesign.com/) - great open source 3D printer hardware design and community
* [Klipper](https://github.com/Klipper3d/klipper) - great open source 3D printer firmware
* [Klipper Z Calibration](https://github.com/protoloft/klipper_z_calibration) - basis for install scripts
* [Cookiecutter](https://github.com/audreyr/cookiecutter) - project template
* [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) - project template
