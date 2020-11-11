
# !/usr/bin/python
import logging
import os
import signal
import sys
from time import sleep
from pathlib import Path
from evdev import InputDevice, ecodes
from app.controller import RoonController, RoonZone

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s',
                    filename='pifi-remote.log',
                    filemode='w')


def exit_handler(received_signal, frame):
    logging.info("Signaling internal jobs to stop...")


def monitor_remote(zone: RoonZone):
    logging.info("Job monitorRemote started")
    # TODO, find the event device number for our FLIRC
    dev = InputDevice('/dev/input/event20')
    if not dev:
        raise BaseException('could not open DEV')
    for event in dev.read_loop():
        # logging.debug(str(categorize(event)))
        if event.type != ecodes.EV_KEY or event.value != 1:
            sleep(0.05)
            continue
        try:

            logging.debug("Status: {}".format('uninitialized'))
            logging.debug("KeyCode: {}".format(event.code))
            if event.code in [ecodes.KEY_LEFT, 165]:
                pass
            elif event.code in [ecodes.KEY_RIGHT, 163]:
                break
            elif event.code in [ecodes.KEY_UP, 115]:
                pass
            elif event.code in [ecodes.KEY_DOWN, 114]:
                pass
            elif event.code in [ecodes.KEY_ENTER, 164]:
                pass
            elif event.code in [ecodes.KEY_ESC, 166]:
                pass
            elif event.code in [51]:
                break
            elif event.code == 51:
                break
            else:
                logging.debug('unknown key code')
        except Exception as e:
            logging.error("Caught exception: %s (%s)", e , type(e))
    logging.info("Job monitorRemote stopped")


def main():
    logging.info("starting %s", __file__)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    controller = RoonController(Path('app_info.json'), Path('.roon-token'))
    zone = controller.get_zone('Wohnzimmer')
    logging.info('successfully opened zone: Wohnzimmer')
    zone.pause()
    zone.play()
    zone.skip()
    controller._safe_token()
    del controller

    try:
        monitor_remote()
    except Exception as e:
        logging.error("Critical exception: %s", e)

    logging.info("terminated")
    exit(0)


if __name__ == '__main__':
    main()
