"""Class handling the logic and commands provided by an Roon output!"""
import json
import logging
from typing import Dict, List

from .controller import RoonApi

logger = logging.getLogger('zone')


class RoonOutputE(BaseException):
    """Basic Class for Output """
    def __init__(self, msg):
        self.msg = msg


class RoonOutput:
    """Implment logic for Roon Outputs"""

    EVENT_FILTER = ['outputs_changed', 'zones_changed']

    def __init__(self, api: RoonApi, output_name: str, register_callback=False):
        super(RoonOutput).__init__()
        self._api = api
        self._name = output_name
        self._oid = None
        oid = self._get_output_id(output_name)
        if not oid:
            raise RoonOutputE('could not find any output with name "{}"'.format(output_name))

        self._oid = oid
        if register_callback:
            logger.debug('enabling callback for zone updates')
            self._api.register_state_callback(self._callback,
                                              event_filter=self.EVENT_FILTER,
                                              id_filter=None)
        logger.debug('instantiated RoonOutput {}'.format(output_name))

    def _callback(self, event: str, ids_changed: List):
        """Callback for debugging purposes."""
        logger.debug('==> callback triggered: {} => {}'.format(event, repr(ids_changed)))
        if 'zones_changed' in event:
            for zid_changed in ids_changed:
                if zid_changed == self._get_zone_id():
                    logger.debug('==> change for current ZID detected {}'.format(self._oid))
                    logger.debug('==> {}'.format(json.dumps(self._api.zones[zid_changed], indent=2)))
        elif 'outputs_changed' in event:
            for oid_changed in ids_changed:
                if oid_changed == self._oid:
                    logger.debug('==> change for current OID detected')
                    logger.debug('==> {}'.format(json.dumps(self._api.outputs[oid_changed], indent=2)))
        logger.debug("==> FINISHED <==\n")
        pass

    @property
    def zone_id(self):
        if self._oid and self._oid in self._api.outputs.keys():
            return self._api.outputs[self._oid]['zone_id']
        else:
            logger.error('failed to retrieve the ZID for given OID "{}"'.format(self._oid))
            return None

    @property
    def state(self):
        z = self.zone_id
        if z and z in self._api.zones.keys():
            return self._api.zones[z]['state']
        else:
            logger.error('failed to retrieve the state for OID {}'.format(self._oid))
            return None

    def _get_output_id(self, name: str):
        """Try to find the OID based on names."""
        logger.debug('finding output "{}"'.format(name))
        o = self._api.output_by_name(name)
        if not o:
            logger.error('could not find output "{}"'.format(name))
            return None
        oid = o['output_id']
        zid = o['zone_id']
        logger.debug('found output {} with ID {} in ZONE {}'.format(name, oid, zid))
        return oid

    def _get_output(self) -> Dict:
        """Simplify the access to the output dictionary for current OID"""
        if self._oid in self._api.outputs.keys():
            return self._api.outputs[self._oid]
        else:
            return {}

    def _get_zone_id(self) -> str:
        output = self._get_output()
        if not output:
            logger.error('failed to retrieve output DICT for {}'. format(self._oid))
        zid = output['zone_id']
        logger.debug('==> found ZID {} for OID {}'.format(zid, self._oid))
        return zid

    def pause(self):
        """Next Track"""
        self._api.playback_control(self.zone_id, "pause")

    def stop(self):
        """Stop Player and Clear Playlist"""
        self._api.playback_control(self.zone_id, "stop")
        self._api.seek(self.zone_id, 0)

    def playpause(self):
        self._api.playback_control(self.zone_id, "playpause")

    def repeat(self, repeat: bool):
        logger.debug(f"{'enable' if repeat else 'disable'} for zone {self.zone_id}")
        self._api.repeat(self.zone_id, repeat)

    def play(self):
        """Start Play with current playlist"""
        self._api.playback_control(self.zone_id, "play")

    def skip(self):
        """Skip current title"""
        self._api.playback_control(self.zone_id, "next")

    def previous(self):
        self._api.playback_control(self.zone_id, "previous")

    def volume_up(self, value: int = 5):
        self._api.mute(self._oid, False)
        self._api.change_volume(self._oid, value, method="relative_step")

    def volume_down(self, value: int = 5):
        self._api.mute(self._oid, False)
        self._api.change_volume(self._oid, -1 * value, method="relative_step")

    def mute(self, enabled=False):
        self._api.mute(self._oid, enabled)

    def play_playlist(self, playlist_name, volume: int = 20):
        logger.debug("play_playlist: %s" % playlist_name)
        self.stop()
        self._api.mute(self._oid, False)
        self._api.change_volume(self._oid, volume, method="absolute")
        self._api.shuffle(self.zone_id, shuffle=False)
        self._api.repeat(self.zone_id, repeat=True)
        # path = ['Library', 'Artists', 'Sting', 'The Bridge']
        path = ['My Live Radio', 'Radio Paradise (320k aac)']
        if not self._api.play_media(self.zone_id, path, action="Play Now"):
            logger.error(f"Failed to media for : {repr(path)}")

    def play_radio_station(self, station_name: str):
        """
        Play a certain radio station
        """
        logger.debug("play radio: %s" % station_name)
        self.stop()
        self._api.change_volume(self._oid, 20, method="absolute")
        path = ['My Live Radio', station_name]
        self._api.play_media(self.zone_id, path=path, action="Play Now")

    def is_muted(self) -> bool:
        """Return True if output is muted, otherwise False."""
        o = self._get_output()
        if 'volume' in o.keys():
            return o['volume']['is_muted']
        else:
            return False
