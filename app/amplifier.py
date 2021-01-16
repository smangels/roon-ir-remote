
import requests
from typing import Dict
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger("yamaha")
logger.setLevel(logging.DEBUG)


class AmplifierE(BaseException):

    def __init__(self, msg):
        self._msg = msg


class Amplifier(ABC):
    """An abstract class for amplifiers"""

    def __init__(self, config: Dict):
        self._config = config
        self._hostname = config.get('hostname')
        self._type = config.get('type')
        self._initiated = False
        super().__init__()

    @abstractmethod
    def mute(self) -> bool:
        raise AmplifierE('not implemented')

    @abstractmethod
    def unmute(self) -> bool:
        raise AmplifierE('unmute, not yet implemented')

    @abstractmethod
    def set_volume(self, level_percent: int) -> bool:
        raise AmplifierE('set_volume, not yet implemented')


class Yamaha(Amplifier):
    """Provide simplified access to Yamaha Rest API"""

    def __init__(self, config, zone="main", api_version='v1'):
        super(Yamaha, self).__init__(config=config)
        self._api_version = api_version
        self._zone = zone
        self._url = '/'.join(["http:/", self._hostname, "YamahaExtendedControl", self._api_version, self._zone])
        self._status = {}

        status = self._request(ep="getStatus", args=None)
        self._status = status
        self._initiated = True

        logger.debug("initiated Yamaha instance: {}".format(self._hostname))

    def __str__(self):
        return "/".join([self._url, "getStatus"])

    def _generate_endpoint(self, endpoint, args=None) -> str:
        ep = "/".join([self._url, endpoint])
        if args:
            ep = "?".join([ep, args])
        logger.debug("generated EP: {}".format(ep))
        return ep

    def _request(self, ep, args=None) -> Dict:
        _ep = self._generate_endpoint(endpoint=ep, args=args)
        logger.debug('sending request => %s' % _ep)
        result = requests.get(_ep)
        if 200 <= result.status_code <= 300:
            return result.json()
        else:
            raise BaseException()

    def _mute_control(self, enabled=False) -> bool:
        _enabled = "true" if enabled else "false"
        self._request(ep="setMute", args="enable={}".format(_enabled))
        return True

    def set_volume(self, level_percent: int) -> bool:
        """Set volume for a main zone"""
        absolute = (level_percent / 100) * self._status['max_volume']
        self._request(ep="setVolume", args="volume={}".format(int(absolute)))
        return True

    def mute(self) -> bool:
        """mute the main zone."""
        return self._mute_control(enabled=True)

    def unmute(self) -> bool:
        """unmute the main zone"""
        return self._mute_control(enabled=False)
