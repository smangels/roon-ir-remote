
# !/usr/bin/python
import logging
import signal
import sys
from pathlib import Path

import evdev
from evdev import InputDevice

from app import RoonController, RoonZone, RemoteConfig

INPUT_DEVICE = None
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s')


# TODO: making variables part of the signal handler
# TODO: stop loop over select
def exit_handler(received_signal, frame):
    global INPUT_DEVICE
    logging.info("Signaling internal jobs to stop...")
    sys.exit(0)


def get_event_device_for_string(dev_name: str):
    """Scan the Input Device tree for Flirc unit and return the device"""
    dev = None
    logging.debug('looking for input device "{}"'.format(dev_name))
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if 'flirc Keyboard' in device.name:
            dev = device
            logging.debug('found FLIRC device on path: {}'.format(device.name, device.path))
            break
    return dev


def monitor_remote(zone: RoonZone, dev: InputDevice):
    '''start an event loop in InputDevice'''
    logging.info("Job monitorRemote started")

    if not dev:
        raise BaseException('could not open DEV')
    global INPUT_DEVICE
    INPUT_DEVICE = dev
    logging.debug('opening InputDevice: {}'.format(dev.name))
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

        except Exception as e:
            logging.error("Caught exception: %s (%s)", e , type(e))
    logging.info("Job monitorRemote stopped")


def main():
    logging.info("starting %s", __file__)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    event_dev = get_event_device_for_string('flirc Keyboard')

    if not event_dev:
        logging.error('Could not find any event device')
        sys.exit(1)

    logging.debug('found event device: {}'.format(event_dev))

    config = RemoteConfig(Path('app_info.json'))

    controller = RoonController(config.app_info, Path('.roon-token'))

    zone = controller.get_zone(config.zone)

    logging.info('successfully opened zone: Wohnzimmer')

    try:
        monitor_remote(zone, event_dev)
    except Exception as e:
        logging.error("Critical exception: %s", e)

    controller.shutdown()
    logging.info("terminated")
    exit(0)


if __name__ == '__main__':
    main()
