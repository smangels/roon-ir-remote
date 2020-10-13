
from roonapi import RoonApi
import json
import sys
import signal
import curses
from typing import Dict
from time import sleep


class RoonScreen:
    """
    Control a screen using curses
    """
    def __init__(self):
        super(RoonScreen).__init__()
        self._mainwin = None
        self._initiate_stdscr()

    def _initiate_stdscr(self) -> curses:
        self._mainwin = curses.initscr()
        self._mainwin.keypad(0)
        self._mainwin.refresh()
        curses.noecho()     # do not echo keyboard input
        curses.cbreak()     # react on keyboard input immediately
        self._mainwin.refresh()

    def refresh(self):
        self._mainwin.refresh()

    def my_state_callback(*args, **kwargs):
        """
        Update the status display when
        """
        print('state changed: {}'.format(args))

    def update_status(self, txt: str) -> None:
        self._mainwin.addstr(txt + '\n')
        self._mainwin.refresh()

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        curses.nocbreak()
        self._mainwin.keypad(False)
        curses.echo()
        curses.endwin()


def read_as_json(path) -> Dict:
    _data = {}
    with open(path) as f:
        _data = json.load(f)
    return _data


appinfo = read_as_json('app_info.json')
token = open('mytokenfile').read()

api = RoonApi(appinfo, token)
screen = RoonScreen()
screen.update_status('connecting to Roon server....')


# get all zones (as dict)
zones = api.zones

for zone in zones:

    # we need the output ID for the zone
    oid = zones[zone]['outputs'][0]['output_id']
    volume = api.outputs[oid]['volume']['value']
    screen.update_status('zone: {}, volume: {}'.format(zones[zone]['display_name'], volume))

sleep(2)
# receive state updates in your callback
api.register_state_callback(RoonScreen.my_state_callback)

screen.shutdown()

# save the token for next time
with open('mytokenfile', 'w') as f:
    f.write(api.token)
