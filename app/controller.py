import json
from pathlib import Path
from typing import Dict, Tuple, Type
from typing import List
from typing import Tuple
import logging

from roonapi import RoonApi, RoonDiscovery

from .token import RoonToken
from .output import RoonOutput

logger = logging.getLogger('roon-controller')
logger.setLevel(logging.DEBUG)


class RoonControllerE(BaseException):
    def __init__(self, msg):
        super(RoonControllerE, self).__init__()
        self.msg = msg


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

        server = self._discover_server()
        logger.debug("Received: %s" % server[0])

        if not server:
            logger.error("failed to discover a server")
            raise RoonControllerE("failed to discover a Roon server")

        if token:
            self._token = RoonToken(token)

        if self._token.is_empty():
            self._api = RoonApi(self._info, token=None, host=server[0], port=server[1])
        else:
            self._api = RoonApi(self._info, token=self._token.to_string(), host=server[0], port=server[1])

        if self._api:
            self._token.set(self._api.token)
            logger.debug("Connected to API: %s, %s, %s" % (self._api.host, self._api.core_name, self._api.core_id))

        logger.debug('instantiated a Roon controller on: %s' % self._api.core_name)

    @staticmethod
    def _discover_server() -> Tuple:
        """
        Run the discovery that allows us to detect the server,
        return the very first server discovered.
        """
        discover = RoonDiscovery(None)
        servers = discover.all()
        logger.debug("Discovery found: %s" % repr(servers))
        discover.stop()
        if not servers:
            logger.debug('failed to discover Roon server')
            return None, 0

        return servers[0]

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
