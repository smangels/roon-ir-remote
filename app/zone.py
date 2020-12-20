
from .controller import RoonApi
from typing import Dict
import logging


class RoonZone:

    def __init__(self, api: RoonApi, zone: Dict, register_callback=False):
        super(RoonZone).__init__()
        self._api = api
        self._zone = zone
        self._zone_id = self._get_zone_id()
        if register_callback:
            self._api.register_state_callback(self.callback,
                                              event_filter=['zones_changed'],
                                              id_filter=[self._zone_id]
                                              )

    def callback(self, *args, **kwargs):
        print('==> callback triggered: {}'.format(args))
        for item in args:
            print('  {}'.format(item))

    def status(self):
        """retrieve the current status of a zone"""
        pass

    def _get_zone_id(self):
        return self._zone['zone_id']

    def pause(self):
        """Next Track"""
        self._api.playback_control(self._zone_id, "pause")

    def stop(self):
        """Stop Player and Clear Playlist"""
        self._api.playback_control(self._zone_id, "stop")

    def playpause(self):
        self._api.playback_control(self._zone_id, "playpause")

    def mute(self):
        self._api.mute(self._zone_id, True)

    def play(self):
        """Start Play with current playlist"""
        self._api.playback_control(self._zone_id, "play")

    def skip(self):
        """Skip current title"""
        self._api.playback_control(self._zone_id, "next")

    def previous(self):
        self._api.playback_control(self._zone_id, "previous")

    def volume_up(self, value: int = 5):
        self._api.change_volume(self._zone_id, value, method="relative")

    def volume_down(self, value: int = 5):
        self._api.change_volume(self._zone_id, ((-1) * value), method="relative")
