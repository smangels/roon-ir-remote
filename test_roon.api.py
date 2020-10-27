import sys
from pathlib import Path

from app import RoonController


def main():
    app = RoonController(Path('app_info.json'))

    # run the application
    app.run()

    # register a signal and shutdown
    app.shutdown()


if __name__ == '__main__':
    sys.exit(main())

