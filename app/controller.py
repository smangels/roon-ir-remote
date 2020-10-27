import json
from pathlib import Path
from typing import Dict
from time import sleep

from roonapi import RoonApi

from .roon_screen import ScreenTerminal
from .token import RoonToken


class RoonController(object):
    """
    Roon Controller, initiate buttons, display and RoonAPI
    """

    def __init__(self, app_info: Path, token: Path = '.roon-token'):
        super(RoonController, self).__init__()
        self._info = RoonController._read_as_json(app_info)
        token_path = Path(token)
        token = RoonToken(token_path)
        self._api = RoonApi(self._info, str(token))
        self._screen = ScreenTerminal()

    @staticmethod
    def _read_as_json(path) -> Dict:
        _data = {}
        with open(path) as f:
            _data = json.load(f)
        return _data

    def run(self):
        """
        Initiate the display, buttons and start a forever-loop
        """
        self._screen.update_status('connecting to Roon server....')

        # get all zones (as dict)
        zones = self._api.zones

        for zone in zones:
            # we need the output ID for the zone
            oid = zones[zone]['outputs'][0]['output_id']
            volume = self._api.outputs[oid]['volume']['value']
            self._screen.update_status('zone: {}, volume: {}'.format(zones[zone]['display_name'], volume))

        # wait before shutdown
        sleep(5)
        # receive state updates in your callback

    def shutdown(self):
        """
        Shutdown the infinite loop
        """
        self._screen.shutdown()
        self._api.stop()
        pass

