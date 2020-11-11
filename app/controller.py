import json
from pathlib import Path
from time import sleep
from typing import Dict
from typing import List

from roonapi import RoonApi

from .token import RoonToken
from .zone import RoonZone


class RoonController(object):
    """
    Roon Controller, initiate buttons, display and RoonAPI
    """

    def __init__(self, app_info: Path, token: Path = '.roon-token'):
        super(RoonController, self).__init__()
        self._info = RoonController._read_as_json(app_info)
        self._token_path = token
        self._token = None
        if token and token.exists():
            self._token = RoonToken(token)
        if self._token.is_empty():
            self._api = RoonApi(self._info, token=None)
        else:
            self._api = RoonApi(self._info, token=self._token.to_string())
        self._zone = None

    def zones(self) -> List:
        return self._api.zones.keys()

    def get_zone(self, name: str) -> RoonZone:
        z = self._api.zone_by_name(name)
        zone = RoonZone(self._api, z)
        return zone

    @staticmethod
    def _read_as_json(path) -> Dict:
        _data = {}
        with open(path) as f:
            _data = json.load(f)
        return _data

    def _safe_token(self):
        if self._api.token:
            with self._token_path.open(mode='w') as f:
                f.write(self._api.token)

    def shutdown(self):
        """
        Shutdown the infinite loop, save the token
        """
        self._safe_token()
        self._api.stop()

    def __del__(self):
        self._safe_token()
        self._api.stop()


