"""
Implement RoonToken, simply read and write token
"""
from pathlib import Path


class RoonToken:

    def __init__(self, path: Path):
        super(RoonToken, self).__init__()
        self._token = ""
        self.token = ""
        self._path = path
        self._token = RoonToken.read_from_file(self._path)

    @staticmethod
    def read_from_file(path: Path) -> str:
        token = ""
        if path.exists():
            token = path.open().read()
        return token

    def is_empty(self):
        if not self._token:
            return True
        return False

    def to_string(self):
        return str(self._token)

    def set(self, token: str) -> None:
        """set the token and write"""
        with self._path.open('w') as f:
            f.write(token)

    def __str__(self):
        return str(self._token)



