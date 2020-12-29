
from .controller import RoonApi
from typing import Dict, List
import logging
import json

logger = logging.getLogger('zone')


class RoonOutputE(BaseException):

    def __init__(self, msg):
        self.msg = msg


class RoonOutput:

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
            self._api.register_state_callback(self.callback,
                                              event_filter=self.EVENT_FILTER,
                                              id_filter=None)
        logger.debug('instantiated RoonOutput {}'.format(output_name))

    def callback(self, event: str, ids_changed: List):
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
        return self._api.outputs[self._oid]['zone_id']

    def status(self):
        """retrieve the current status of a zone"""
        pass

    def _get_output_id(self, name: str):
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

    def playpause(self):
        self._api.playback_control(self.zone_id, "playpause")

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

    def mute(self):
        self._api.mute(self._oid, True)

    def play_playlist(self, playlist_name):
        self._api.mute(self._oid, False)
        self._api.change_volume(self._oid, 20, method="absolute")
        self._api.play_playlist(self.zone_id, playlist_title=playlist_name)
        self._api.shuffle(self.zone_id, shuffle=False)
        self._api.repeat(self.zone_id, repeat=True)
