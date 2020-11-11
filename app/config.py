
import json
from json import JSONDecodeError
from typing import Dict
from pathlib import Path


class RemoteConfig:

    def __init__(self, path: Path):
        super(RemoteConfig).__init__()
        if not path.exists():
            raise Exception('invalid path given')
        self._config = RemoteConfig._read_as_json(path)

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
        return self._config['roon']['app_info']

    @property
    def zone(self):
        return self._config['roon']['zone']['name']
