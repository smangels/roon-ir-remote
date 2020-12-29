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

from app import RoonController, RoonOutput, RemoteConfig, RemoteConfigE, RemoteKeycodeMapping

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(module)s: %(message)s')
logger = logging.getLogger('roon_remote')


def exit_handler(_received_signal, _frame):
    """Handle SIGINT and SIGTERM signals"""
    logger.info("Signaling internal jobs to stop...")
    sys.exit(0)


def get_event_device_for_string(dev_name: str):
    """Scan the Input Device tree for Flirc unit and return the device"""
    dev = None
    logger.debug('looking for input device "%s"', dev_name)
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        logger.error('no device found, invalid permissions?')
        return None
    for device in devices:
        logger.debug("name: %s" % device.name)
        if dev_name in device.name:
            dev = device
            logger.debug('found device with name: "%s" on path: %s', device.name, device.path)
            break
    return dev


def monitor_remote(zone: RoonOutput, dev: InputDevice, mapping: RemoteKeycodeMapping):
    """start an event loop on InputDevice"""
    logger.info("Job monitorRemote started")

    if not dev:
        raise BaseException('could not open DEV')

    logger.debug('opening exclusively InputDevice: %s', dev.path)
    for event in dev.read_loop():

        if event.value != 1:
            # ignore everything that is not KEY_DOWN
            continue

        # logging.debug(str(categorize(event)))
        try:
            # logging.debug("Status: {}".format('uninitialized'))
            # logging.debug("KeyCode: {}".format(event.code))
            if event.code in mapping.to_key_code('prev'):
                zone.previous()
            elif event.code in mapping.to_key_code('skip'):
                zone.skip()
            elif event.code in mapping.to_key_code('stop'):
                zone.stop()
            elif event.code in mapping.to_key_code('play_pause'):
                if zone.state == "playing":
                    zone.pause()
                else:
                    zone.play()
            elif event.code in mapping.to_key_code('vol_up'):
                zone.volume_up(5)
            elif event.code in mapping.to_key_code('vol_down'):
                zone.volume_down(5)
            elif event.code in mapping.to_key_code('mute'):
                zone.mute(not zone.is_muted())
            elif event.code in mapping.to_key_code('fall_asleep'):
                zone.play_playlist('wellenrauschen')

            logger.debug("Received Code: %s", repr(event.code))

        except Exception as exception:
            logging.error("Caught exception: %s (%s)", exception, type(exception))
    logger.info("Job monitorRemote stopped")


def main():
    """main function, initiate InputDevice and runs the forever loop"""
    logger.info("starting %s", __file__)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    try:
        config = RemoteConfig(Path('app_info.json'))
    except RemoteConfigE as ex:
        logging.error(ex.msg)
        sys.exit(1)

    mapping = config.key_mapping
    logging.info(mapping.edge)

    input_dev_name = "flirc Keyboard"
    event_dev = get_event_device_for_string(input_dev_name)
    if not event_dev:
        logging.error('Could not find any InputDevice with name: "%s"', input_dev_name)
        sys.exit(1)

    logging.debug('found input device: %s', event_dev)

    controller = RoonController(config.app_info, Path('.roon-token'))
    output = controller.get_output(config.zone)
    if not output:
        logging.error('failed to find zone "{}"'.format(config.zone))
        sys.exit(1)

    try:
        monitor_remote(output, event_dev, config.key_mapping)
    except Exception as exception:
        logging.error("Critical exception: %s", exception)

    controller.shutdown()
    logging.info("terminated")
    sys.exit(0)


if __name__ == '__main__':
    main()
