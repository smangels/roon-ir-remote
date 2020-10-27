"""
Implement RoonToken, simply read and write token
"""
from pathlib import Path


class RoonToken:

    def __init__(self, path: Path):
        super(RoonToken, self).__init__()
        self._token = ""
        self._path = path
        self._token = RoonToken.read_from_file(self._path)
        self.initiated = True

    @staticmethod
    def read_from_file(path: Path) -> str:
        token = ""
        if path.exists():
            token = path.open().read()
        return token

    def _safe2file(self):
        with self._path.open('w') as f:
            f.write(self._token)

    def __del__(self):
        self._safe2file()

    def __str__(self):
        return str(self._token)
