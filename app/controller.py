import json
from pathlib import Path
from typing import Dict
from typing import List
import logging

from roonapi import RoonApi

from .token import RoonToken
from .output import RoonOutput, RoonOutputE


logger = logging.getLogger('roon-controller')


class RoonController(object):
    """
    Roon Controller, initiate buttons, display and RoonAPI
    """

    def __init__(self, app_info: Dict, token: Path = '.roon-token'):
        super(RoonController, self).__init__()
        self._info = app_info
        self._token_path = token
        self._token = None
        self._zone = None

        if token:
            self._token = RoonToken(token)

        if self._token.is_empty():
            self._api = RoonApi(self._info, token=None)
        else:
            self._api = RoonApi(self._info, token=self._token.to_string())

        if self._api:
            self._token.set(self._api.token)

        logger.debug('instantiated a Roon controller: %s' % self._api.core_name)

    def zones(self) -> List:
        return self._api.zones.keys()

    def get_output(self, name: str) -> RoonOutput:
        return RoonOutput(self._api, name, register_callback=False)

    @staticmethod
    def _read_as_json(path) -> Dict:
        _data = {}
        with open(path) as f:
            _data = json.load(f)
        return _data

    def shutdown(self):
        """
        Shutdown the infinite loop, save the token
        """
        self._api.stop()

    def __del__(self):
        self._api.stop()
