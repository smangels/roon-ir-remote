"""
Implement a Roon Remote extension that reads keybaord events
from a FLIRC device and converts those events into transport
commands towards a certain _Zone_ in Roon.
"""
# !/usr/bin/python
import logging
import signal
import sys
from pathlib import Path

import evdev
from evdev import InputDevice

from app import RoonController, RoonZone, RemoteConfig

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s')


def exit_handler(_received_signal, _frame):
    """Handle SIGINT and SIGTERM signals"""
    logging.info("Signaling internal jobs to stop...")
    sys.exit(0)


def get_event_device_for_string(dev_name: str):
    """Scan the Input Device tree for Flirc unit and return the device"""
    dev = None
    logging.debug('looking for input device "%s"', dev_name)
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 'flirc Keyboard' in device.name:
            dev = device
            logging.debug('found device with name: "%s" on path: %s', device.name, device.path)
            break
    return dev


def monitor_remote(zone: RoonZone, dev: InputDevice):
    """start an event loop in InputDevice"""
    logging.info("Job monitorRemote started")

    if not dev:
        raise BaseException('could not open DEV')

    logging.debug('opening InputDevice: %s', dev.name)
    for event in dev.read_loop():

        if event.value != 1:
            # ignore everything that is not KEY_DOWN
            continue

        # logging.debug(str(categorize(event)))
        try:
            # logging.debug("Status: {}".format('uninitialized'))
            # logging.debug("KeyCode: {}".format(event.code))
            if event.code in [51]:
                zone.previous()
            elif event.code in [52]:
                zone.skip()
            elif event.code in [45]:
                zone.stop()
            elif event.code in [57]:
                zone.playpause()

        except Exception as exception:
            logging.error("Caught exception: %s (%s)", exception, type(exception))
    logging.info("Job monitorRemote stopped")


def main():
    """main function, initiate InputDevice and runs the forever loop"""
    logging.info("starting %s", __file__)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    event_dev = get_event_device_for_string('flirc Keyboard')

    if not event_dev:
        logging.error('Could not find any event device')
        sys.exit(1)

    logging.debug('found event device: %s', event_dev)

    config = RemoteConfig(Path('app_info.json'))

    controller = RoonController(config.app_info, Path('.roon-token'))

    zone = controller.get_zone(config.zone)

    logging.info('successfully opened zone: %s', config.zone)

    try:
        monitor_remote(zone, event_dev)
    except Exception as exception:
        logging.error("Critical exception: %s", exception)

    controller.shutdown()
    logging.info("terminated")
    sys.exit(0)


if __name__ == '__main__':
    main()
