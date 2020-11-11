
from .controller import RoonApi
from typing import Dict


class RoonZone:

    def __init__(self, api: RoonApi, zone: Dict):
        super(RoonZone).__init__()
        self._api = api
        self._zone = zone
        zone_id = self._get_zone_id()
        self._api.register_state_callback(self.callback,
                                          event_filter=['zones_changed'],
                                          id_filter=[zone_id]
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
        zone_id = self._get_zone_id()
        self._api.playback_control(zone_id, "pause")

    def stop(self):
        """Stop Player and Clear Playlist"""
        zone_id = self._get_zone_id()
        self._api.playback_control(zone_id, "stop")
        pass

    def mute(self):
        zone_id = self._get_zone_id()
        self._api.mute(zone_id, True)

    def play(self):
        """Start Play with current playlist"""
        zone_id = self._get_zone_id()
        self._api.playback_control(zone_id, "play")
        pass

    def skip(self):
        """Skip current title"""
        zone_id = self._get_zone_id()
        self._api.playback_control(zone_id, "next")

    def get_now_playing(self, kind='one_line'):
        pass

    def previous(self):
        zone_id = self._get_zone_id()
        self._api.playback_control(zone_id, "previous")


