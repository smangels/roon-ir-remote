
import curses
from abc import ABC


class RoonScreen(ABC):
    """
    Abstract class implementing basic display features
    """
    def update_status(self, content: str):
        raise NotImplemented()

    def shutdown(self):
        raise NotImplemented()


class ScreenTerminal(RoonScreen):
    """
    Control a screen using curses
    """
    def __init__(self):
        super(RoonScreen).__init__()
        self._main_window = None
        self._initiate_stdscr()

    def _initiate_stdscr(self):
        self._main_window = curses.initscr()
        self._main_window.keypad(0)
        self._main_window.refresh()
        curses.noecho()     # do not echo keyboard input
        curses.cbreak()     # react on keyboard input immediately
        self._main_window.refresh()

    def refresh(self):
        self._main_window.refresh()

    def my_state_callback(*args, **kwargs):
        """
        Update the status display when
        """
        print('state changed: {}'.format(args))

    def update_status(self, txt: str) -> None:
        self._main_window.addstr(txt + '\n')
        self._main_window.refresh()

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        curses.nocbreak()
        self._main_window.keypad(False)
        curses.echo()
        curses.endwin()
