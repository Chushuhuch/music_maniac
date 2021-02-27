from typing import Optional

import yandex_music

from bot import MediaObject, MediaType, logger, MusicService
from musicServices.common import MusicServiceManager


class YandexMusicManager(MusicServiceManager):

    def __init__(self):
        self.client = yandex_music.Client()

    def parseMediaFromLink(self, link: str) -> Optional['MediaObject']:
        raise NotImplementedError

    def searchMediaByLink(self, mediaObject: MediaObject):
        if mediaObject.mediaType != MediaType.TRACK:
            raise NotImplementedError

        search_result = self.client.search(text = '{album}{track}'.format(album = mediaObject.album + ' ' if mediaObject.album else '', track = mediaObject.track), nocorrect = True, type_ = 'track')
        track_results = search_result.tracks
        if not track_results:
            logger.debug('Not found any tracks by the request')
            return
        tracks = track_results.results
        matching_tracks = [track for track in tracks if (not mediaObject.album or len([album for album in track.albums if album.title == mediaObject.album]) > 0) and track.title == mediaObject.track]
        if len(matching_tracks) != 1:
            logger.debug('Found bad amount of tracks in Yandex.Music: {matching_tracks}'.format(matching_tracks = matching_tracks))
        if matching_tracks:
            mediaObject.link[MusicService.YANDEX] = 'https://music.yandex.ru/track/{track_id}'.format(track_id = matching_tracks[0].id)