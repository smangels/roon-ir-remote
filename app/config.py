
import json
from json import JSONDecodeError
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger('RemoteConfig')


class RemoteConfigE(BaseException):
    """ implement a basic exception for config related issues"""

    def __init__(self, msg):
        super(RemoteConfigE, self).__init__()
        self.msg = msg


class RemoteKeycodeMapping:
    """
    contains the configured mapping from keyboard codes to Roon transport actions
    """
    EDGE_UP = "UP"
    EDGE_DOWN = "DOWN"

    def __init__(self, mapping_dict: Dict):
        if 'codes' not in mapping_dict.keys():
            raise RemoteConfigE('codes not found')
        self._dict = mapping_dict
        if 'edge' not in mapping_dict.keys():
            logger.info('no "edge" config detected, setting default UP ')
            self._dict['edge'] = self.EDGE_UP

    @property
    def edge(self) -> str:
        key_name = "edge"
        if key_name not in self._dict.keys():
            raise RemoteConfigE('no key "edge" detected in config')
        return self._dict[key_name]

    def to_key_code(self, transport_action: str) -> List[int]:
        """
        convert transport action into key codes

        Args:
            transport_action (str): one of 'play', 'stop', 'skip', 'prev', 'playpause'
        """
        if 'codes' not in self._dict.keys():
            raise RemoteConfigE('no "codes" key found')

        if transport_action not in self._dict['codes'].keys():
            raise RemoteConfigE(f'no {transport_action} key found')

        return self._dict['codes'][transport_action]


class RemoteConfig:
    """
    Provides an interface to the config file structure
    """

    def __init__(self, path_config_file: Path):
        super(RemoteConfig).__init__()
        logger.debug(path_config_file.absolute())
        if not path_config_file.exists():
            raise RemoteConfigE('RemoteConfig, invalid path given: {}'.format(path_config_file))
        self._config = RemoteConfig._read_as_json(path_config_file)['roon']
        logger.debug('successfully read config from %s', path_config_file)

    @staticmethod
    def _read_as_json(path: Path) -> Dict:
        """Open a file and return JSON content"""
        data = {}
        with path.open(mode='r') as f:
            try:
                data = json.load(f)
            except JSONDecodeError as ex:
                pass
        return data

    @property
    def app_info(self):
        return self._config['app_info']

    @property
    def zone(self):
        return self._config['zone']['name']

    @property
    def amplifier(self):
        if 'amplifier' in self._config['zone'].keys():
            return self._config['zone']['amplifier']
        else:
            return None

    @property
    def key_mapping(self) -> RemoteKeycodeMapping:
        """return a keycode mapping object"""
        return RemoteKeycodeMapping(self._config['event_mapping'])
